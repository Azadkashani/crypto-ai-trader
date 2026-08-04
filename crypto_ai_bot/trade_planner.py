"""
Crypto AI Bot v1.2
Institutional‑Grade Trade Planner – Safe extraction, no dict-float errors
"""

import numpy as np
import pandas as pd
from config import MIN_RISK_REWARD


class TradePlanner:
    def __init__(self, config):
        self.min_rr = config.MIN_RISK_REWARD
        self.atr_buffer_factor = 0.2
        self.cluster_atr_mult = 0.3
        self.max_targets = 3
        self.min_sl_distance_atr = 0.5

    # -----------------------------------------------------------------
    def plan(self, df: pd.DataFrame, market_structure: dict,
             advanced_data: dict, action: str, entry_price: float) -> dict:
        side = "buy" if "BUY" in action else "sell"
        atr = df["ATR"].iloc[-1]

        # 1. محاسبهٔ حد ضرر (فقط یک بار، با مقادیر امن)
        sl = self._calculate_stop_loss(side, entry_price, atr, market_structure, advanced_data)

        # 2. اهداف (با مرتب‌سازی)
        targets = self._calculate_targets(side, entry_price, atr, sl, market_structure, advanced_data)

        # 3. اعتبارسنجی
        valid = False
        rr = 0.0
        reward = 0.0
        risk = abs(entry_price - sl)
        if risk == 0:
            return self._invalid_plan(entry_price, sl, "Risk is zero.")

        for t in targets:
            t_rr = abs(t["price"] - entry_price) / risk
            t["rr"] = round(t_rr, 2)
            if t_rr >= self.min_rr and t["probability"] >= 0.3:
                valid = True
                reward = abs(t["price"] - entry_price)
                rr = t_rr
                break

        if not valid:
            return {
                "entry": entry_price,
                "stop_loss": round(sl, 4),
                "targets": targets,
                "risk": round(risk, 4),
                "reward": 0,
                "rr": 0,
                "valid": False,
                "reasons": [f"No target meets minimum RR ({self.min_rr}) or probability (0.3)."]
            }

        return {
            "entry": entry_price,
            "stop_loss": round(sl, 4),
            "targets": targets,
            "risk": round(risk, 4),
            "reward": round(reward, 4),
            "rr": round(rr, 2),
            "valid": True,
            "reasons": []
        }

    # -----------------------------------------------------------------
    def _calculate_stop_loss(self, side, entry, atr, ms, adv):
        candidates = self._gather_sl_candidates(side, entry, ms, adv)
        if not candidates:
            return self._atr_fallback(side, entry, atr, ms)

        # امتیازدهی و انتخاب بهترین
        for c in candidates:
            c["score"] = self._score_level(c, ms, adv, atr)

        valid = [c for c in candidates if (side == "buy" and c["price"] < entry) or
                                          (side == "sell" and c["price"] > entry)]
        if not valid:
            return self._atr_fallback(side, entry, atr, ms)

        best = max(valid, key=lambda x: x["score"])
        buffer = atr * self.atr_buffer_factor
        if side == "buy":
            sl_candidate = best["price"] - buffer
        else:
            sl_candidate = best["price"] + buffer

        # بررسی حداقل فاصله
        if abs(entry - sl_candidate) < self.min_sl_distance_atr * atr:
            return self._atr_fallback(side, entry, atr, ms)
        return sl_candidate

    def _gather_sl_candidates(self, side, entry, ms, adv):
        cand = []
        # Swing High/Low (با _safe_float)
        for s in ms.get("swing_highs", []):
            price = self._safe_float(s)
            if price is not None:
                cand.append({"price": price, "type": "swing_high"})
        for s in ms.get("swing_lows", []):
            price = self._safe_float(s)
            if price is not None:
                cand.append({"price": price, "type": "swing_low"})

        # Order Blocks (با _safe_float)
        ob = adv.get("order_block") if adv else None
        if ob and ob.get("valid"):
            if ob.get("bullish_ob") and side == "buy":
                price = self._safe_float(ob["bullish_ob"].get("low"))
                if price: cand.append({"price": price, "type": "ob_bullish"})
            if ob.get("bearish_ob") and side == "sell":
                price = self._safe_float(ob["bearish_ob"].get("high"))
                if price: cand.append({"price": price, "type": "ob_bearish"})

        # SR Strength (با _safe_float)
        sr = adv.get("sr_strength") if adv else None
        if sr:
            if side == "buy" and sr.get("valid_support"):
                price = self._safe_float(sr.get("support_level"))
                if price: cand.append({"price": price, "type": "support_50"})
            if side == "sell" and sr.get("valid_resistance"):
                price = self._safe_float(sr.get("resistance_level"))
                if price: cand.append({"price": price, "type": "resistance_50"})

        # FVG (با _safe_float)
        fvg = adv.get("fvg") if adv else None
        if fvg and fvg.get("active_fvg"):
            act = fvg["active_fvg"]
            if side == "buy" and act["type"] == "bullish":
                price = self._safe_float(act.get("gap_low"))
                if price: cand.append({"price": price, "type": "fvg_bullish"})
            if side == "sell" and act["type"] == "bearish":
                price = self._safe_float(act.get("gap_high"))
                if price: cand.append({"price": price, "type": "fvg_bearish"})

        # POC (با _safe_float)
        vp = adv.get("volume_profile") if adv else None
        if vp:
            poc = self._safe_float(vp.get("poc"))
            if poc and ((side == "buy" and poc < entry) or (side == "sell" and poc > entry)):
                cand.append({"price": poc, "type": "poc"})
        return cand

    def _safe_float(self, value):
        """تبدیل ایمن به float؛ دیکشنری‌ها را هم پشتیبانی می‌کند."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, dict):
            # گاهی swing یک دیکشنری با کلید price است
            return float(value.get("price", value.get("value", 0.0)))
        try:
            return float(value)
        except:
            return None

    def _score_level(self, cand, ms, adv, atr):
        weights = {
            "swing_low": 0.9, "swing_high": 0.9,
            "ob_bullish": 0.85, "ob_bearish": 0.85,
            "support_50": 0.7, "resistance_50": 0.7,
            "fvg_bullish": 0.6, "fvg_bearish": 0.6,
            "poc": 0.5
        }
        return weights.get(cand["type"], 0.5)

    def _atr_fallback(self, side, entry, atr, ms):
        mult = 1.5 if ms.get("trend") in ("bullish", "bearish") else 2.0
        if side == "buy":
            return entry - atr * mult
        else:
            return entry + atr * mult

    # -----------------------------------------------------------------
    def _calculate_targets(self, side, entry, atr, sl, ms, adv):
        raw = self._gather_tp_candidates(side, entry, ms, adv)
        if not raw:
            return [self._atr_target(side, entry, atr, sl, emergency=True)]

        clusters = self._cluster_levels(raw, atr)
        for cl in clusters:
            cl["score"] = self._score_cluster(cl, side, entry, ms, adv)
            best = max(cl["members"], key=lambda x: x.get("quality", 0.5))
            cl["price"] = self._safe_float(best["price"])

        clusters.sort(key=lambda x: x["score"], reverse=True)
        chosen = clusters[:self.max_targets]

        targets = []
        for cl in chosen:
            prob = self._estimate_probability(cl, side, entry, atr, ms)
            targets.append({
                "price": round(cl["price"], 4),
                "pct": round((cl["price"] / entry - 1) * 100, 2) if side == "buy"
                       else round((entry / cl["price"] - 1) * 100, 2),
                "rr": 0.0,
                "probability": round(prob, 2),
                "label": ""
            })

        if not targets:
            targets = [self._atr_target(side, entry, atr, sl, emergency=True)]
            return targets

        # مرتب‌سازی بر اساس نزدیکی
        if side == "buy":
            targets.sort(key=lambda x: x["price"])
        else:
            targets.sort(key=lambda x: x["price"], reverse=True)

        for i, t in enumerate(targets):
            t["label"] = f"TP{i+1}"

        return targets

    def _gather_tp_candidates(self, side, entry, ms, adv):
        levels = []
        # Swing
        for s in ms.get("swing_highs", []):
            p = self._safe_float(s)
            if p and ((side == "buy" and p > entry) or (side == "sell" and p < entry)):
                levels.append({"price": p, "type": "swing_high", "quality": 0.9})
        for s in ms.get("swing_lows", []):
            p = self._safe_float(s)
            if p and ((side == "sell" and p < entry) or (side == "buy" and p > entry)):
                levels.append({"price": p, "type": "swing_low", "quality": 0.9})

        # Order Blocks
        ob = adv.get("order_block") if adv else None
        if ob and ob.get("valid"):
            if side == "buy" and ob.get("bearish_ob"):
                p = self._safe_float(ob["bearish_ob"].get("high"))
                if p and p > entry: levels.append({"price": p, "type": "ob_bearish", "quality": 0.85})
            if side == "sell" and ob.get("bullish_ob"):
                p = self._safe_float(ob["bullish_ob"].get("low"))
                if p and p < entry: levels.append({"price": p, "type": "ob_bullish", "quality": 0.85})

        # SR
        sr = adv.get("sr_strength") if adv else None
        if sr:
            if side == "buy" and sr.get("valid_resistance"):
                p = self._safe_float(sr.get("resistance_level"))
                if p and p > entry: levels.append({"price": p, "type": "resistance_50", "quality": 0.75})
            if side == "sell" and sr.get("valid_support"):
                p = self._safe_float(sr.get("support_level"))
                if p and p < entry: levels.append({"price": p, "type": "support_50", "quality": 0.75})

        # FVG
        fvg = adv.get("fvg") if adv else None
        if fvg and fvg.get("active_fvg"):
            act = fvg["active_fvg"]
            if side == "buy" and act["type"] == "bearish":
                p = self._safe_float(act.get("gap_high"))
                if p and p > entry: levels.append({"price": p, "type": "fvg_bearish", "quality": 0.7})
            if side == "sell" and act["type"] == "bullish":
                p = self._safe_float(act.get("gap_low"))
                if p and p < entry: levels.append({"price": p, "type": "fvg_bullish", "quality": 0.7})

        # VWAP
        vwap_data = adv.get("vwap") if adv else None
        if vwap_data:
            p = self._safe_float(vwap_data.get("vwap"))
            if p and ((side == "buy" and p > entry) or (side == "sell" and p < entry)):
                levels.append({"price": p, "type": "vwap", "quality": 0.6})

        # POC
        vp = adv.get("volume_profile") if adv else None
        if vp:
            p = self._safe_float(vp.get("poc"))
            if p and ((side == "buy" and p > entry) or (side == "sell" and p < entry)):
                levels.append({"price": p, "type": "poc", "quality": 0.5})

        # Fibonacci
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

    def _cluster_levels(self, levels, atr):
        if not levels: return []
        levels_sorted = sorted(levels, key=lambda x: x["price"])
        threshold = atr * self.cluster_atr_mult
        clusters = []
        current = [levels_sorted[0]]
        for lvl in levels_sorted[1:]:
            if lvl["price"] - current[-1]["price"] <= threshold:
                current.append(lvl)
            else:
                clusters.append({"members": current})
                current = [lvl]
        clusters.append({"members": current})
        return clusters

    def _score_cluster(self, cluster, side, entry, ms, adv):
        total_q = sum(m.get("quality", 0.5) for m in cluster["members"])
        avg_q = total_q / len(cluster["members"])
        size_bonus = min(0.2, 0.05 * len(cluster["members"]))
        score = avg_q + size_bonus
        dist = abs(cluster["members"][0]["price"] - entry)
        if dist < 0.5 * adv.get("atr_volatility", {}).get("atr_ratio", 1):
            score *= 0.8
        return min(1.0, score)

    def _estimate_probability(self, cluster, side, entry, atr, ms):
        base = cluster["score"] * 0.7
        dist = abs(cluster["price"] - entry) / atr if atr > 0 else 1
        dist_factor = max(0.2, 1 - 0.1 * dist)
        strength = ms.get("strength", "Medium")
        trend_bonus = 0.15 if strength == "Very Strong" else 0.1 if strength == "Strong" else 0.0
        prob = base * dist_factor + trend_bonus
        return min(0.95, max(0.05, prob))

    def _atr_target(self, side, entry, atr, sl, emergency=False):
        tp_price = entry + atr * 2 if side == "buy" else entry - atr * 2
        rr = abs(tp_price - entry) / abs(entry - sl) if abs(entry - sl) > 0 else 2.0
        return {
            "price": round(tp_price, 4),
            "pct": round(atr / entry * 2 * 100, 2),
            "rr": round(rr, 2),
            "probability": 0.1 if emergency else 0.3,
            "label": "TP1 (ATR fallback)" if emergency else "TP1 (ATR)"
        }

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
