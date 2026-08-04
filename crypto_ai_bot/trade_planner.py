"""
Crypto AI Bot v1.2
Institutional‑Grade Trade Planner – Wider Stop/Target Margins, Optimized EV
"""

import numpy as np
import pandas as pd
from config import MIN_RISK_REWARD


class TradePlanner:
    def __init__(self, config):
        self.min_rr = config.MIN_RISK_REWARD
        self.atr_buffer_factor = 0.2
        self.cluster_pct = 0.1
        self.max_targets = 3
        self.min_sl_distance_atr = 0.8          # افزایش یافت
        self.min_target_distance_atr = 0.8       # افزایش یافت

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
        # 2. Gather all TP candidates (filtered with min_target_distance)
        tp_candidates = self._gather_tp_candidates(side, entry, atr, ms=market_structure, adv=advanced_data)

        if not tp_candidates:
            tp_candidates = self._atr_fallback_targets(side, entry, atr, count=3)

        clustered_tp = self._cluster_levels(tp_candidates, entry, atr)

        if side == "buy":
            clustered_tp.sort(key=lambda x: x["price"])
        else:
            clustered_tp.sort(key=lambda x: x["price"], reverse=True)

        chosen_targets = self._select_independent_targets(clustered_tp, atr, entry, side)

        for i, t in enumerate(chosen_targets):
            t["label"] = f"TP{i+1}"
            t["probability"] = self._estimate_probability(t["price"], entry, atr, market_structure, advanced_data, side)

        while len(chosen_targets) < self.max_targets:
            fallback = self._create_atr_target(side, entry, atr, len(chosen_targets)+1)
            if fallback:
                fallback["probability"] = self._estimate_probability(fallback["price"], entry, atr, market_structure, advanced_data, side)
                chosen_targets.append(fallback)

        for t in chosen_targets:
            self._normalize_target(t, entry, side)

        best_plan = self._optimize_sl_and_validate(entry, sl_candidates, chosen_targets, side, atr, market_structure)

        for t in best_plan["targets"]:
            self._normalize_target(t, entry, side)
            if best_plan["stop_loss"] is not None:
                risk = abs(entry - best_plan["stop_loss"])
                t["rr"] = round(abs(t["price"] - entry) / risk, 2) if risk > 0 else 0.0
        return best_plan

    # -----------------------------------------------------------------
    @staticmethod
    def _normalize_target(target, entry, side):
        if "label" not in target:
            target["label"] = "TP"
        if "pct" not in target:
            if side == "buy":
                target["pct"] = round((target["price"] / entry - 1) * 100, 2)
            else:
                target["pct"] = round((entry / target["price"] - 1) * 100, 2)
        if "rr" not in target:
            target["rr"] = 0.0
        if "probability" not in target:
            target["probability"] = 0.5
        return target

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

    # --- SL candidates unchanged except increased min_sl_distance_atr used in validation ---
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

        atr_val = 0.001
        cand.append({"price": self._atr_sl(side, entry, atr_val, ms), "type": "atr"})
        return cand

    def _atr_sl(self, side, entry, atr, ms):
        mult = 1.5 if ms.get("trend") in ("bullish", "bearish") else 2.0
        if side == "buy":
            return entry - atr * mult
        else:
            return entry + atr * mult

    # --- TP candidates with increased min distance ---
    def _gather_tp_candidates(self, side, entry, atr, ms, adv):
        levels = []
        min_dist = atr * self.min_target_distance_atr
        for s in ms.get("swing_highs", []):
            p = self._safe_float(s)
            if p and ((side == "buy" and p > entry + min_dist) or (side == "sell" and p < entry - min_dist)):
                levels.append({"price": p, "type": "swing_high", "quality": 0.9})
        for s in ms.get("swing_lows", []):
            p = self._safe_float(s)
            if p and ((side == "sell" and p < entry - min_dist) or (side == "buy" and p > entry + min_dist)):
                levels.append({"price": p, "type": "swing_low", "quality": 0.9})

        ob = adv.get("order_block") if adv else None
        if ob and ob.get("valid"):
            if side == "buy" and ob.get("bearish_ob"):
                p = self._safe_float(ob["bearish_ob"])
                if p and p > entry + min_dist: levels.append({"price": p, "type": "ob_bearish", "quality": 0.85})
            if side == "sell" and ob.get("bullish_ob"):
                p = self._safe_float(ob["bullish_ob"])
                if p and p < entry - min_dist: levels.append({"price": p, "type": "ob_bullish", "quality": 0.85})

        sr = adv.get("sr_strength") if adv else None
        if sr:
            if side == "buy" and sr.get("valid_resistance"):
                p = self._safe_float(sr.get("resistance_level"))
                if p and p > entry + min_dist: levels.append({"price": p, "type": "resistance_50", "quality": 0.75})
            if side == "sell" and sr.get("valid_support"):
                p = self._safe_float(sr.get("support_level"))
                if p and p < entry - min_dist: levels.append({"price": p, "type": "support_50", "quality": 0.75})

        fvg = adv.get("fvg") if adv else None
        if fvg and fvg.get("active_fvg"):
            act = fvg["active_fvg"]
            if side == "buy" and act["type"] == "bearish":
                p = self._safe_float(act.get("gap_high"))
                if p and p > entry + min_dist: levels.append({"price": p, "type": "fvg_bearish", "quality": 0.7})
            if side == "sell" and act["type"] == "bullish":
                p = self._safe_float(act.get("gap_low"))
                if p and p < entry - min_dist: levels.append({"price": p, "type": "fvg_bullish", "quality": 0.7})

        vwap_data = adv.get("vwap") if adv else None
        if vwap_data:
            p = self._safe_float(vwap_data.get("vwap"))
            if p and ((side == "buy" and p > entry + min_dist) or (side == "sell" and p < entry - min_dist)):
                levels.append({"price": p, "type": "vwap", "quality": 0.6})

        vp = adv.get("volume_profile") if adv else None
        if vp:
            p = self._safe_float(vp.get("poc"))
            if p and ((side == "buy" and p > entry + min_dist) or (side == "sell" and p < entry - min_dist)):
                levels.append({"price": p, "type": "poc", "quality": 0.5})

        fib = adv.get("fibonacci") if adv else None
        if fib and fib.get("levels"):
            for lvl in ["1.272", "1.618"]:
                p = self._safe_float(fib["levels"].get(lvl))
                if p and ((side == "buy" and p > entry + min_dist) or (side == "sell" and p < entry - min_dist)):
                    levels.append({"price": p, "type": f"fib_{lvl}", "quality": 0.65})
            for lvl in ["0.618", "0.786"]:
                p = self._safe_float(fib["levels"].get(lvl))
                if p and ((side == "sell" and p < entry - min_dist) or (side == "buy" and p > entry + min_dist)):
                    levels.append({"price": p, "type": f"fib_{lvl}", "quality": 0.65})

        return levels

    # --- Clustering, selection, fallback unchanged ---
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

    def _select_independent_targets(self, clustered, atr, entry, side):
        selected = []
        for level in clustered:
            if all(abs(level["price"] - s["price"]) > atr * 0.5 for s in selected):
                selected.append(level)
            if len(selected) >= self.max_targets:
                break
        return selected

    def _atr_fallback_targets(self, side, entry, atr, count=3):
        mults = [1.5, 2.5, 4.0]
        targets = []
        for i, mult in enumerate(mults[:count]):
            if side == "buy":
                tp = entry + atr * mult
            else:
                tp = entry - atr * mult
            targets.append({"price": tp, "type": "atr", "quality": 0.3, "label": f"TP{i+1} (ATR)"})
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

    def _optimize_sl_and_validate(self, entry, sl_candidates, targets, side, atr, ms):
        best_ev = -999
        best_sl = None
        best_target = None
        best_reward = 0
        best_rr = 0
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
                    ev = prob * rr - (1 - prob)
                    if ev > best_ev:
                        best_ev = ev
                        best_rr = rr
                        best_reward = reward
                        best_sl = sl_price
                        best_target = t

        if best_sl is not None:
            risk_final = abs(entry - best_sl)
            for t in targets:
                t["rr"] = round(abs(t["price"] - entry) / risk_final, 2) if risk_final > 0 else 0.0
            return {
                "entry": entry,
                "stop_loss": round(best_sl, 4),
                "targets": targets,
                "risk": round(risk_final, 4),
                "reward": round(best_reward, 4),
                "rr": round(best_rr, 2),
                "valid": True,
                "reasons": reasons
            }

        atr_sl = self._atr_sl(side, entry, atr, ms)
        risk_fallback = abs(entry - atr_sl)
        max_rr = 0
        for t in targets:
            rr = abs(t["price"] - entry) / risk_fallback if risk_fallback > 0 else 0
            if rr > max_rr: max_rr = rr
        for t in targets:
            t["rr"] = round(abs(t["price"] - entry) / risk_fallback, 2) if risk_fallback > 0 else 0.0
        reasons.append(f"No target meets minimum RR ({self.min_rr}) with any valid stop loss.")
        return {
            "entry": entry,
            "stop_loss": round(atr_sl, 4),
            "targets": targets,
            "risk": round(risk_fallback, 4),
            "reward": 0,
            "rr": round(max_rr, 2),
            "valid": False,
            "reasons": reasons
        }
