"""
Crypto AI Bot v1.2
Institutional‑Grade Trade Planner – Dynamic SL, multi‑TP, probability scoring, EV optimisation
"""

import numpy as np
import pandas as pd
from config import MIN_RISK_REWARD


class TradePlanner:
    def __init__(self, config):
        self.min_rr = config.MIN_RISK_REWARD
        self.atr_buffer_factor = 0.2          # safety margin below/above a level
        self.cluster_atr_mult = 0.3           # clustering threshold (fraction of ATR)
        self.max_targets = 3
        self.volatility_lookback = 20

    # -----------------------------------------------------------------
    # Public entry point
    # -----------------------------------------------------------------
    def plan(self, df: pd.DataFrame, market_structure: dict,
             advanced_data: dict, action: str, entry_price: float) -> dict:
        """
        Returns
        -------
        dict with keys:
            entry, stop_loss, targets (list of dicts), risk, reward, rr,
            valid (bool), reasons (list of str)
        """
        side = "buy" if "BUY" in action else "sell"
        atr = df["ATR"].iloc[-1]

        # 1. Calculate a single, high‑quality stop loss ---------------------------------
        sl = self._calculate_stop_loss(
            side, entry_price, atr, market_structure, advanced_data
        )

        # 2. Gather, cluster, score, and rank possible targets -------------------------
        targets = self._calculate_targets(
            side, entry_price, atr, sl, market_structure, advanced_data
        )

        # 3. Compute risk/reward based on the closest target (TP1) ----------------------
        tp1 = targets[0]["price"] if targets else None
        if tp1 is None:
            return self._invalid_plan(entry_price, sl, "No valid target found.")

        risk = abs(entry_price - sl)
        reward = abs(tp1 - entry_price)
        rr = reward / risk if risk > 0 else 0.0

        # 4. Validate the trade --------------------------------------------------------
        valid, reasons = self._validate_trade(
            side, entry_price, sl, tp1, rr, market_structure, advanced_data, targets
        )

        return {
            "entry": entry_price,
            "stop_loss": round(sl, 4),
            "targets": targets,
            "risk": round(risk, 4),
            "reward": round(reward, 4),
            "rr": round(rr, 2),
            "valid": valid,
            "reasons": reasons
        }

    # -----------------------------------------------------------------
    # STOP LOSS – scored candidates, ATR buffer only as safety
    # -----------------------------------------------------------------
    def _calculate_stop_loss(self, side: str, entry: float, atr: float,
                             ms: dict, adv: dict) -> float:
        """Return a single, high‑quality stop‑loss price."""
        # Collect candidate supports/resistances
        candidates = self._gather_sl_candidates(side, entry, ms, adv)
        if not candidates:
            return self._atr_fallback(side, entry, atr, ms)

        # Score each candidate
        for cand in candidates:
            cand["score"] = self._score_level(cand, ms, adv, atr)

        # For a buy, we need the strongest support **below** entry.
        # For a sell, the strongest resistance **above** entry.
        valid = [c for c in candidates if (side == "buy" and c["price"] < entry) or
                                          (side == "sell" and c["price"] > entry)]
        if not valid:
            return self._atr_fallback(side, entry, atr, ms)

        # Select candidate with highest quality score
        best = max(valid, key=lambda x: x["score"])

        # Add a small ATR safety buffer beyond the level
        buffer = atr * self.atr_buffer_factor
        if side == "buy":
            return best["price"] - buffer
        else:
            return best["price"] + buffer

    def _gather_sl_candidates(self, side, entry, ms, adv):
        """Gather all potential stop‑loss levels from market structure and advanced data."""
        cand = []
        # Swing points
        swing_highs = [{"price": p, "type": "swing_high"} for p in ms.get("swing_highs", [])]
        swing_lows  = [{"price": p, "type": "swing_low"}  for p in ms.get("swing_lows", [])]
        if side == "buy":
            cand.extend(swing_lows)
        else:
            cand.extend(swing_highs)

        # Order Blocks
        ob = adv.get("order_block") if adv else None
        if ob and ob.get("valid"):
            if ob.get("bullish_ob") and side == "buy":
                cand.append({"price": ob["bullish_ob"]["low"], "type": "ob_bullish"})
            if ob.get("bearish_ob") and side == "sell":
                cand.append({"price": ob["bearish_ob"]["high"], "type": "ob_bearish"})

        # SR Strength
        sr = adv.get("sr_strength") if adv else None
        if sr:
            if side == "buy" and sr.get("valid_support"):
                cand.append({"price": sr.get("support_level"), "type": "support_50"})
            if side == "sell" and sr.get("valid_resistance"):
                cand.append({"price": sr.get("resistance_level"), "type": "resistance_50"})

        # FVG extremes
        fvg = adv.get("fvg") if adv else None
        if fvg and fvg.get("active_fvg"):
            if side == "buy" and fvg["active_fvg"]["type"] == "bullish":
                cand.append({"price": fvg["active_fvg"]["gap_low"], "type": "fvg_bullish"})
            if side == "sell" and fvg["active_fvg"]["type"] == "bearish":
                cand.append({"price": fvg["active_fvg"]["gap_high"], "type": "fvg_bearish"})

        # Volume Profile POC (only if directionally favourable)
        vp = adv.get("volume_profile") if adv else None
        if vp and vp.get("poc"):
            poc = vp["poc"]
            if (side == "buy" and poc < entry) or (side == "sell" and poc > entry):
                cand.append({"price": poc, "type": "poc"})

        return cand

    def _score_level(self, cand, ms, adv, atr):
        """Compute a quality score (0‑1) for a level."""
        # Base weight depends on type
        weights = {
            "swing_low": 0.9, "swing_high": 0.9,
            "ob_bullish": 0.85, "ob_bearish": 0.85,
            "support_50": 0.7, "resistance_50": 0.7,
            "fvg_bullish": 0.6, "fvg_bearish": 0.6,
            "poc": 0.5
        }
        score = weights.get(cand["type"], 0.5)

        # Boost if level is part of a BOS/CHoCH (using market structure context)
        # (Simplified: if level is a recent swing high/low, give higher weight)
        if "swing" in cand["type"]:
            score *= 1.1

        # Distance penalty (closer levels are more relevant)
        # Placeholder: no distance penalty for SL selection (we already filter direction)
        return min(1.0, score)

    def _atr_fallback(self, side, entry, atr, ms):
        """Fallback SL based on ATR and volatility regime."""
        # Adjust multiplier by market regime (trending vs ranging)
        regime = ms.get("trend", "sideways")
        if regime == "bullish" or regime == "bearish":
            mult = 1.5
        else:
            mult = 2.0
        if side == "buy":
            return entry - atr * mult
        else:
            return entry + atr * mult

    # -----------------------------------------------------------------
    # TARGETS – clustering, scoring, ranking, probability assignment
    # -----------------------------------------------------------------
    def _calculate_targets(self, side, entry, atr, sl,
                           ms, adv):
        """Return a list of target dicts, sorted by priority (TP1, TP2, TP3)."""
        # 1. Gather all potential target levels (resistances for buy, supports for sell)
        raw_levels = self._gather_tp_candidates(side, entry, ms, adv)
        if not raw_levels:
            return [self._atr_target(side, entry, atr, sl)]

        # 2. Cluster levels that are very close to each other
        clusters = self._cluster_levels(raw_levels, atr)

        # 3. Score each cluster and assign a representative price
        for cl in clusters:
            cl["score"] = self._score_cluster(cl, side, entry, ms, adv)
            # representative = level with highest individual score within cluster
            best = max(cl["members"], key=lambda x: x.get("quality", 0.5))
            cl["price"] = best["price"]

        # 4. Rank clusters by score (descending)
        clusters.sort(key=lambda x: x["score"], reverse=True)

        # 5. Select top N targets, compute probability, RR, etc.
        targets = []
        for i, cl in enumerate(clusters[:self.max_targets]):
            prob = self._estimate_probability(cl, side, entry, atr, ms)
            tp_rr = abs(cl["price"] - entry) / abs(entry - sl) if abs(entry - sl) > 0 else 0
            targets.append({
                "price": round(cl["price"], 4),
                "pct": round((cl["price"] / entry - 1) * 100, 2) if side == "buy"
                       else round((entry / cl["price"] - 1) * 100, 2),
                "rr": round(tp_rr, 2),
                "probability": round(prob, 2),
                "label": f"TP{i+1}"
            })

        # 6. If no clusters selected, fallback to ATR based target
        if not targets:
            targets = [self._atr_target(side, entry, atr, sl)]
        return targets

    def _gather_tp_candidates(self, side, entry, ms, adv):
        """Return list of dicts with price, type, quality from all sources."""
        levels = []

        # Swing highs/lows
        for p in ms.get("swing_highs", []):
            if side == "buy" and p > entry:
                levels.append({"price": p, "type": "swing_high"})
        for p in ms.get("swing_lows", []):
            if side == "sell" and p < entry:
                levels.append({"price": p, "type": "swing_low"})

        # Order blocks
        ob = adv.get("order_block") if adv else None
        if ob and ob.get("valid"):
            if side == "buy" and ob.get("bearish_ob"):
                levels.append({"price": ob["bearish_ob"]["high"], "type": "ob_bearish"})
            if side == "sell" and ob.get("bullish_ob"):
                levels.append({"price": ob["bullish_ob"]["low"], "type": "ob_bullish"})

        # SR Strength
        sr = adv.get("sr_strength") if adv else None
        if sr:
            if side == "buy" and sr.get("valid_resistance"):
                levels.append({"price": sr.get("resistance_level"), "type": "resistance_50"})
            if side == "sell" and sr.get("valid_support"):
                levels.append({"price": sr.get("support_level"), "type": "support_50"})

        # FVG extremes (opposite side)
        fvg = adv.get("fvg") if adv else None
        if fvg and fvg.get("active_fvg"):
            if side == "buy" and fvg["active_fvg"]["type"] == "bearish":
                levels.append({"price": fvg["active_fvg"]["gap_high"], "type": "fvg_bearish"})
            if side == "sell" and fvg["active_fvg"]["type"] == "bullish":
                levels.append({"price": fvg["active_fvg"]["gap_low"], "type": "fvg_bullish"})

        # VWAP
        vwap_data = adv.get("vwap") if adv else None
        if vwap_data and vwap_data.get("vwap"):
            levels.append({"price": vwap_data["vwap"], "type": "vwap"})

        # POC
        vp = adv.get("volume_profile") if adv else None
        if vp and vp.get("poc"):
            levels.append({"price": vp["poc"], "type": "poc"})

        # Fibonacci levels (context‑aware)
        fib = adv.get("fibonacci") if adv else None
        if fib and fib.get("levels"):
            # Use only extension levels 1.272, 1.618 for buy; retracement for sell
            if side == "buy":
                for lvl in ["1.272", "1.618"]:
                    if lvl in fib["levels"] and fib["levels"][lvl] > entry:
                        levels.append({"price": fib["levels"][lvl], "type": f"fib_{lvl}"})
            else:
                for lvl in ["0.618", "0.786"]:
                    if lvl in fib["levels"] and fib["levels"][lvl] < entry:
                        levels.append({"price": fib["levels"][lvl], "type": f"fib_{lvl}"})

        # Attach a basic quality weight
        type_quality = {
            "swing_high": 0.9, "swing_low": 0.9,
            "ob_bearish": 0.85, "ob_bullish": 0.85,
            "resistance_50": 0.75, "support_50": 0.75,
            "fvg_bearish": 0.7, "fvg_bullish": 0.7,
            "vwap": 0.6, "poc": 0.5,
            "fib_1.272": 0.65, "fib_1.618": 0.65,
            "fib_0.618": 0.65, "fib_0.786": 0.65
        }
        for lvl in levels:
            lvl["quality"] = type_quality.get(lvl["type"], 0.5)

        return levels

    def _cluster_levels(self, levels, atr):
        """Group nearby levels into clusters (distance < cluster_atr_mult * ATR)."""
        if not levels:
            return []
        # Sort by price ascending
        levels_sorted = sorted(levels, key=lambda x: x["price"])
        threshold = atr * self.cluster_atr_mult
        clusters = []
        current_cluster = [levels_sorted[0]]
        for lvl in levels_sorted[1:]:
            if lvl["price"] - current_cluster[-1]["price"] <= threshold:
                current_cluster.append(lvl)
            else:
                clusters.append({"members": current_cluster})
                current_cluster = [lvl]
        clusters.append({"members": current_cluster})
        return clusters

    def _score_cluster(self, cluster, side, entry, ms, adv):
        """Score a cluster based on its members' quality, size, and structure."""
        # Combine member qualities (weighted average)
        total_q = sum(m.get("quality", 0.5) for m in cluster["members"])
        avg_q = total_q / len(cluster["members"])
        # Bonus for more members (confluence)
        size_bonus = min(0.2, 0.05 * len(cluster["members"]))
        score = avg_q + size_bonus
        # Penalty if cluster is too close to entry (noise)
        dist = abs(cluster["members"][0]["price"] - entry)
        if dist < 0.5 * adv.get("atr_volatility", {}).get("atr_ratio", 1):
            score *= 0.8
        return min(1.0, score)

    def _estimate_probability(self, cluster, side, entry, atr, ms):
        """Estimate the probability that price reaches the cluster's level."""
        base_prob = cluster["score"] * 0.7  # structural quality
        # Distance factor (farther targets less likely)
        dist = abs(cluster["price"] - entry) / atr if atr > 0 else 1
        dist_factor = max(0.2, 1 - 0.1 * dist)
        # Trend strength bonus
        strength = ms.get("strength", "Medium")
        if strength == "Very Strong":
            trend_bonus = 0.15
        elif strength == "Strong":
            trend_bonus = 0.1
        else:
            trend_bonus = 0.0
        prob = base_prob * dist_factor + trend_bonus
        return min(0.95, max(0.05, prob))

    def _atr_target(self, side, entry, atr, sl):
        """ATR‑based fallback target when no structural targets found."""
        tp_price = entry + atr * 2 if side == "buy" else entry - atr * 2
        rr = abs(tp_price - entry) / abs(entry - sl) if abs(entry - sl) > 0 else 2.0
        return {
            "price": round(tp_price, 4),
            "pct": round(atr / entry * 2 * 100, 2),
            "rr": round(rr, 2),
            "probability": 0.3,
            "label": "TP1 (ATR fallback)"
        }

    # -----------------------------------------------------------------
    # TRADE VALIDATION (beyond simple RR)
    # -----------------------------------------------------------------
    def _validate_trade(self, side, entry, sl, tp, rr, ms, adv, targets):
        reasons = []
        valid = True

        # 1. Minimum RR
        if rr < self.min_rr:
            reasons.append(f"RR ({rr:.2f}) < {self.min_rr}")
            valid = False

        # 2. SL inside a liquidity pool? (simplified: check if SL is very close to a major swing)
        if side == "buy":
            swing_lows = ms.get("swing_lows", [])
            for low in swing_lows:
                if abs(sl - low) < 0.1 * sl:  # very near a swing low
                    reasons.append("SL dangerously close to swing low (liquidity pool)")
                    valid = False
                    break
        else:
            swing_highs = ms.get("swing_highs", [])
            for high in swing_highs:
                if abs(sl - high) < 0.1 * sl:
                    reasons.append("SL dangerously close to swing high (liquidity pool)")
                    valid = False
                    break

        # 3. TP sitting inside a strong resistance/support cluster (low probability)
        if targets and targets[0]["probability"] < 0.3:
            reasons.append("First target probability too low (<0.3)")
            valid = False

        # 4. Structure quality: if market structure is sideways, reduce confidence
        if ms.get("trend") == "sideways":
            reasons.append("Sideways market – lower conviction")
            # Not invalid, just warning

        # 5. Volume check: if volume Z‑Score < -0.5, add warning (not invalid)
        # (We don't have direct volume Z here, but could be added)

        # 6. Breakout quality poor (fake breakout)
        bq = adv.get("breakout_quality") if adv else None
        if bq and bq.get("quality") == "Fake Breakout":
            reasons.append("Fake breakout – trade risky")
            valid = False

        # 7. Macro risk
        # (handled by scanner, not here)

        return valid, reasons

    # -----------------------------------------------------------------
    # Helper for invalid plan
    # -----------------------------------------------------------------
    def _invalid_plan(self, entry, sl, reason):
        return {
            "entry": entry,
            "stop_loss": sl,
            "targets": [],
            "risk": 0,
            "reward": 0,
            "rr": 0,
            "valid": False,
            "reasons": [reason]
        }
