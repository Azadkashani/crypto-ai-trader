"""
Crypto AI Bot v1.2
Institutional‑Grade Trade Planner – Normalized Targets, Robust
"""

import numpy as np
import pandas as pd
from config import MIN_RISK_REWARD


class TradePlanner:
    def __init__(self, config):
        self.min_rr = config.MIN_RISK_REWARD
        self.atr_buffer_factor = 0.2
        self.cluster_pct = 0.1              # cluster levels closer than 0.1% of price
        self.max_targets = 3
        self.min_sl_distance_atr = 0.5

    # -----------------------------------------------------------------
    def plan(self, df: pd.DataFrame, market_structure: dict,
             advanced_data: dict, action: str, entry_price: float) -> dict:
        try:
            entry = float(entry_price)
        except:
            entry = 0.0
        try:
            atr = float(df["ATR"].iloc[-1])
        except:
            atr = 0.001

        side = "buy" if "BUY" in action else "sell"

        # 1. Gather all SL candidates
        sl_candidates = self._gather_sl_candidates(side, entry, ms=market_structure, adv=advanced_data)
        # 2. Gather all TP candidates
        tp_candidates = self._gather_tp_candidates(side, entry, ms=market_structure, adv=advanced_data)

        # If no TP candidates, create ATR fallback set
        if not tp_candidates:
            tp_candidates = self._atr_fallback_targets(side, entry, atr, count=3)

        # Cluster TP candidates (only very close duplicates)
        clustered_tp = self._cluster_levels(tp_candidates, entry, atr)

        # Sort by distance from entry (nearest first)
        if side == "buy":
            clustered_tp.sort(key=lambda x: x["price"])   # ascending
        else:
            clustered_tp.sort(key=lambda x: x["price"], reverse=True)  # descending

        # Select up to max_targets independent targets
        chosen_targets = self._select_independent_targets(clustered_tp, atr, entry, side)

        # Assign labels and probabilities
        for i, t in enumerate(chosen_targets):
            t["label"] = f"TP{i+1}"
            t["probability"] = self._estimate_probability(t["price"], entry, atr, market_structure, advanced_data, side)

        # Ensure at least max_targets (fill with ATR if needed)
        while len(chosen_targets) < self.max_targets:
            fallback = self._create_atr_target(side, entry, atr, len(chosen_targets)+1)
            if fallback:
                fallback["probability"] = self._estimate_probability(fallback["price"], entry, atr, market_structure, advanced_data, side)
                chosen_targets.append(fallback)

        # Normalize all targets (ensure pct, rr, label, probability exist)
        for t in chosen_targets:
            self._normalize_target(t, entry, side)

        # 3. Optimize SL and validate RR
        best_plan = self._optimize_sl_and_validate(entry, sl_candidates, chosen_targets, side, atr, market_structure)

        # Final normalization of all targets in plan
        for t in best_plan["targets"]:
            self._normalize_target(t, entry, side)

        return best_plan

    # -----------------------------------------------------------------
    # Normalize target (ensure all required keys exist)
    # -----------------------------------------------------------------
    @staticmethod
    def _normalize_target(target, entry, side):
        # label
        if "label" not in target:
            target["label"] = "TP"
        # pct
        if "pct" not in target:
            if side == "buy":
                target["pct"] = round((target["price"] / entry - 1) * 100, 2)
            else:
                target["pct"] = round((entry / target["price"] - 1) * 100, 2)
        # rr (will be updated later, set default)
        if "rr" not in target:
            target["rr"] = 0.0
        # probability
        if "probability" not in target:
            target["probability"] = 0.5
        return target

    # -----------------------------------------------------------------
    # Safe float extraction
    # -----------------------------------------------------------------
    @staticmethod
    def _safe_float(value):
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, dict):
            for key in ("price", "value", "close", "open", "high", "low"):
                if key in value:
                    return TradePlanner._safe_float(value[key])
            for v in value.values():
                res = TradePlanner._safe_float(v)
                if res is not None:
                    return res
            return None
        if isinstance(value, (list, tuple)):
            for item in value:
                res = TradePlanner._safe_float(item)
                if res is not None:
                    return res
            return None
        try:
            return float(value)
        except:
            return None

    # -----------------------------------------------------------------
    # Gather Stop Loss candidates
    # -----------------------------------------------------------------
    def _gather_sl_candidates(self, side, entry, ms, adv):
        cand = []
        for s in ms.get("swing_highs", []):
            price = self._safe_float(s)
            if price is not None:
                cand.append({"price": price, "type": "swing_high"})
        for s in ms.get("swing_lows", []):
            price = self._safe_float(s)
            if price is not None:
                cand.append({"price": price, "type": "swing_low"})

        ob = adv.get("order_block") if adv else None
        if ob and ob.get("valid"):
            if ob.get("bullish_ob") and side == "buy":
                price = self._safe_float(ob["bullish_ob"])
                if price: cand.append({"price": price, "type": "ob_bullish"})
            if ob.get("bearish_ob") and side == "sell":
                price = self._safe_float(ob["bearish_ob"])
                if price: cand.append({"price": price, "type": "ob_bearish"})

        sr = adv.get("sr_strength") if adv else None
        if sr:
            if side == "buy" and sr.get("valid_support"):
                price = self._safe_float(sr.get("support_level"))
                if price: cand.append({"price": price, "type": "support_50"})
            if side == "sell" and sr.get("valid_resistance"):
                price = self._safe_float(sr.get("resistance_level"))
                if price: cand.append({"price": price, "type": "resistance_50"})

        fvg = adv.get("fvg") if adv else None
        if fvg and fvg.get("active_fvg"):
            act = fvg["active_fvg"]
            if side == "buy" and act["type"] == "bullish":
                price = self._safe_float(act.get("gap_low"))
                if price: cand.append({"price": price, "type": "fvg_bullish"})
            if side == "sell" and act["type"] == "bearish":
                price = self._safe_float(act.get("gap_high"))
                if price: cand.append({"price": price, "type": "fvg_bearish"})

        vp = adv.get("volume_profile") if adv else None
        if vp:
            poc = self._safe_float(vp.get("poc"))
            if poc and ((side == "buy" and poc < entry) or (side == "sell" and poc > entry)):
                cand.append({"price": poc, "type": "poc"})

        atr = 0.001
        cand.append({"price": self._atr_sl(side, entry, atr, ms), "type": "atr"})
        return cand

    def _atr_sl(self, side, entry, atr, ms):
        mult = 1.5 if ms.get("trend") in ("bullish", "bearish") else 2.0
        if side == "buy":
            return entry - atr * mult
        else:
            return entry + atr * mult

    # -----------------------------------------------------------------
    # Gather Take Profit candidates
    # -----------------------------------------------------------------
    def _gather_tp_candidates(self, side, entry, ms, adv):
        levels = []
        for s in ms.get("swing_highs", []):
            p = self._safe_float(s)
            if p and ((side == "buy" and p > entry) or (side == "sell" and p < entry)):
                levels.append({"price": p, "type": "swing_high", "quality": 0.9})
        for s in ms.get("swing_lows", []):
            p = self._safe_float(s)
            if p and ((side == "sell" and p < entry) or (side == "buy" and p > entry)):
                levels.append({"price": p, "type": "swing_low", "quality": 0.9})

        ob = adv.get("order_block") if adv else None
        if ob and ob.get("valid"):
            if side == "buy" and ob.get("bearish_ob"):
                p = self._safe_float(ob["bearish_ob"])
                if p and p > entry: levels.append({"price": p, "type": "ob_bearish", "quality": 0.85})
            if side == "sell" and ob.get("bullish_ob"):
                p = self._safe_float(ob["bullish_ob"])
                if p and p < entry: levels.append({"price": p, "type": "ob_bullish", "quality": 0.85})

        sr = adv.get("sr_strength") if adv else None
        if sr:
            if side == "buy" and sr.get("valid_resistance"):
                p = self._safe_float(sr.get("resistance_level"))
                if p and p > entry: levels.append({"price": p, "type": "resistance_50", "quality": 0.75})
            if side == "sell" and sr.get("valid_support"):
                p = self._safe_float(sr.get("support_level"))
                if p and p < entry: levels.append({"price": p, "type": "support_50", "quality": 0.75})

        fvg = adv.get("fvg") if adv else None
        if fvg and fvg.get("active_fvg"):
            act = fvg["active_fvg"]
            if side == "buy" and act["type"] == "bearish":
                p = self._safe_float(act.get("gap_high"))
                if p and p > entry: levels.append({"price": p, "type": "fvg_bearish", "quality": 0.7})
            if side == "sell" and act["type"] == "bullish":
                p = self._safe_float(act.get("gap_low"))
                if p and p < entry: levels.append({"price": p, "type": "fvg_bullish", "quality": 0.7})

        vwap_data = adv.get("vwap") if adv else None
        if vwap_data:
            p = self._safe_float(vwap_data.get("vwap"))
            if p and ((side == "buy" and p > entry) or (side == "sell" and p < entry)):
                levels.append({"price": p, "type": "vwap", "quality": 0.6})

        vp = adv.get("volume_profile") if adv else None
        if vp:
            p = self._safe_float(vp.get("poc"))
            if p and ((side == "buy" and p > entry) or (side == "sell" and p < entry)):
                levels.append({"price": p, "type": "poc", "quality": 0.5})

        fib = adv.get("fibonacci") if adv else None
        if fib and fib.get("levels"):
            for lvl in ["1.272", "1.618"]:
                p = self._safe_float(fib["levels"].get(lvl))
                if p and ((side == "buy" and p > entry) or (side == "sell" and p < entry)):
                    levels.append({"price": p, "type": f"fib_{lvl}", "quality": 0.65})
            for lvl in ["0.618", "0.786"]:
                p = self._safe_float(fib["levels"].get(lvl))
                if p and ((side == "sell" and p < entry) or (side == "buy" and p > entry)):
                    levels.append({"price": p, "type": f"fib_{lvl}", "quality": 0.65})

        return levels

    # -----------------------------------------------------------------
    # Clustering: merge only very close levels (0.1% of price)
    # -----------------------------------------------------------------
    def _cluster_levels(self, levels, entry, atr):
        if not levels: return []
        threshold = entry * self.cluster_pct / 100.0
        levels_sorted = sorted(levels, key=lambda x: x["price"])
        clusters = []
        current_cluster = [levels_sorted[0]]
        for lvl in levels_sorted[1:]:
            if lvl["price"] - current_cluster[-1]["price"] <= threshold:
                current_cluster.append(lvl)
            else:
                clusters.append({"members": current_cluster})
                current_cluster = [lvl]
        clusters.append({"members": current_cluster})
        result = []
        for cl in clusters:
            best = max(cl["members"], key=lambda x: x.get("quality", 0.5))
            result.append({"price": best["price"], "type": best["type"], "quality": best["quality"]})
        return result

    # -----------------------------------------------------------------
    # Select independent targets (at least ATR distance apart)
    # -----------------------------------------------------------------
    def _select_independent_targets(self, clustered, atr, entry, side):
        selected = []
        for level in clustered:
            if all(abs(level["price"] - s["price"]) > atr * 0.5 for s in selected):
                selected.append(level)
            if len(selected) >= self.max_targets:
                break
        return selected

    # -----------------------------------------------------------------
    # ATR fallback targets (multiple)
    # -----------------------------------------------------------------
    def _atr_fallback_targets(self, side, entry, atr, count=3):
        mults = [1.5, 2.5, 4.0]
        targets = []
        for i, mult in enumerate(mults[:count]):
            if side == "buy":
                tp = entry + atr * mult
            else:
                tp = entry - atr * mult
            target = {"price": tp, "type": "atr", "quality": 0.3, "label": f"TP{i+1} (ATR)"}
            targets.append(target)
        return targets

    def _create_atr_target(self, side, entry, atr, index):
        mults = [1.5, 2.5, 4.0]
        if index-1 < len(mults):
            mult = mults[index-1]
            if side == "buy":
                price = entry + atr * mult
            else:
                price = entry - atr * mult
            return {"price": price, "type": "atr", "quality": 0.3, "label": f"TP{index} (ATR)"}
        return None

    # -----------------------------------------------------------------
    # Probability estimation
    # -----------------------------------------------------------------
    def _estimate_probability(self, target_price, entry, atr, ms, adv, side):
        dist_atr = abs(target_price - entry) / atr if atr > 0 else 1
        if dist_atr <= 1:
            base = 0.7
        elif dist_atr <= 2:
            base = 0.5
        elif dist_atr <= 3:
            base = 0.35
        else:
            base = 0.2

        strength = ms.get("strength", "Medium")
        if strength == "Very Strong":
            base += 0.15
        elif strength == "Strong":
            base += 0.08

        if adv.get("order_block", {}).get("valid"):
            base += 0.05
        if adv.get("fvg", {}).get("active_fvg"):
            base += 0.05
        vp = adv.get("volume_profile")
        if vp and self._safe_float(vp.get("poc")):
            poc = self._safe_float(vp["poc"])
            if abs(target_price - poc) / entry < 0.01:
                base += 0.05

        regime = adv.get("market_regime")
        if regime and "Ranging" in regime.get("regime", ""):
            base *= 0.8

        return round(min(0.95, max(0.05, base)), 2)

    # -----------------------------------------------------------------
    # Optimize SL and validate RR
    # -----------------------------------------------------------------
    def _optimize_sl_and_validate(self, entry, sl_candidates, targets, side, atr, ms):
        best_sl = None
        best_rr = 0
        best_reward = 0
        valid_target = None
        reasons = []

        for sl_cand in sl_candidates:
            sl_price = sl_cand["price"]
            if side == "buy" and sl_price >= entry: continue
            if side == "sell" and sl_price <= entry: continue

            if abs(entry - sl_price) < self.min_sl_distance_atr * atr:
                continue

            risk = abs(entry - sl_price)
            for t in targets:
                reward = abs(t["price"] - entry)
                rr = reward / risk if risk > 0 else 0
                prob = t.get("probability", 0.5)
                if rr >= self.min_rr and prob >= 0.3:
                    if rr > best_rr:
                        best_rr = rr
                        best_reward = reward
                        best_sl = sl_price
                        valid_target = t

        if best_sl is not None and valid_target is not None:
            # update all targets with calculated RR
            for t in targets:
                risk_final = abs(entry - best_sl)
                t["rr"] = round(abs(t["price"] - entry) / risk_final, 2) if risk_final > 0 else 0.0
            return {
                "entry": entry,
                "stop_loss": round(best_sl, 4),
                "targets": targets,
                "risk": round(abs(entry - best_sl), 4),
                "reward": round(best_reward, 4),
                "rr": round(best_rr, 2),
                "valid": True,
                "reasons": reasons
            }

        atr_sl = self._atr_sl(side, entry, atr, ms)
        risk = abs(entry - atr_sl)
        for t in targets:
            reward = abs(t["price"] - entry)
            rr = reward / risk if risk > 0 else 0
            prob = t.get("probability", 0.5)
            if rr >= self.min_rr and prob >= 0.3:
                for t2 in targets:
                    t2["rr"] = round(abs(t2["price"] - entry) / risk, 2) if risk > 0 else 0.0
                return {
                    "entry": entry,
                    "stop_loss": round(atr_sl, 4),
                    "targets": targets,
                    "risk": round(risk, 4),
                    "reward": round(reward, 4),
                    "rr": round(rr, 2),
                    "valid": True,
                    "reasons": []
                }

        reasons.append(f"No target meets minimum RR ({self.min_rr}) with any valid stop loss.")
        return {
            "entry": entry,
            "stop_loss": round(atr_sl, 4) if atr_sl else entry - atr,
            "targets": targets,
            "risk": 0,
            "reward": 0,
            "rr": 0,
            "valid": False,
            "reasons": reasons
        }
