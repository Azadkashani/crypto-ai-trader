"""
Crypto AI Bot v1.2
Trade Planner – Dynamic Entry, Stop Loss, Multi-Target, Realistic Risk/Reward
"""

import numpy as np

class TradePlanner:
    def __init__(self, config):
        self.min_rr = config.MIN_RISK_REWARD

    def plan(self, df, market_structure, advanced_data, action, entry_price):
        """
        برنامه‌ریزی کامل یک معامله بر اساس تحلیل تکنیکال.
        action : 'BUY' | 'SELL' | 'STRONG BUY' | 'STRONG SELL'
        بازگشت: دیکشنری شامل entry, stop_loss, targets, risk, reward, rr, valid, reasons
        """
        side = "buy" if "BUY" in action else "sell"
        atr = df["ATR"].iloc[-1]

        # استخراج سطوح کلیدی از Market Structure و Advanced Analytics
        swing_highs = [h["price"] for h in market_structure.get("swing_highs", [])]
        swing_lows  = [l["price"] for l in market_structure.get("swing_lows", [])]

        # حمایت‌ها و مقاومت‌های استاتیک (۵۰ کندل)
        resistance_50 = df["high"].tail(50).max()
        support_50    = df["low"].tail(50).min()

        # سطوح Order Block
        ob = advanced_data.get("order_block", {}) if advanced_data else {}
        bullish_ob = ob.get("bullish_ob", {}) if ob.get("valid") else None
        bearish_ob = ob.get("bearish_ob", {}) if ob.get("valid") else None

        # FVG
        fvg = advanced_data.get("fvg", {}) if advanced_data else {}
        bullish_fvg = fvg.get("active_fvg") if fvg.get("bullish_fvg") else None
        bearish_fvg = fvg.get("active_fvg") if fvg.get("bearish_fvg") else None

        # Fibonacci (سطوح اصلاحی)
        fib = advanced_data.get("fibonacci", {}) if advanced_data else {}
        fib_levels = fib.get("levels", {})

        # VWAP
        vwap_data = advanced_data.get("vwap", {}) if advanced_data else {}
        vwap = vwap_data.get("vwap")

        # Volume Profile POC
        vp = advanced_data.get("volume_profile", {}) if advanced_data else {}
        poc = vp.get("poc")

        # SR Strength
        sr = advanced_data.get("sr_strength", {}) if advanced_data else {}

        # Breakout Quality
        bq = advanced_data.get("breakout_quality", {}) if advanced_data else {}

        # ----- 1. تعیین Stop Loss -----
        stop_loss = self._calculate_stop_loss(
            side, entry_price, atr,
            swing_lows, swing_highs,
            bullish_ob, bearish_ob,
            support_50, resistance_50,
            sr, poc
        )

        # ----- 2. تعیین اهداف (حداقل ۲ تا ۳ هدف) -----
        targets = self._calculate_targets(
            side, entry_price, atr,
            swing_highs, swing_lows,
            resistance_50, support_50,
            bullish_ob, bearish_ob,
            fvg, vwap, poc, fib_levels
        )

        # ----- 3. محاسبهٔ Risk و Reward (بر اساس نزدیک‌ترین هدف) -----
        if side == "buy":
            risk = entry_price - stop_loss
            # اولین هدف معتبر (TP1)
            tp1 = next((t["price"] for t in targets if t["price"] > entry_price), None)
        else:
            risk = stop_loss - entry_price
            tp1 = next((t["price"] for t in targets if t["price"] < entry_price), None)

        if risk <= 0 or tp1 is None:
            return {
                "entry": entry_price,
                "stop_loss": stop_loss,
                "targets": targets,
                "risk": risk,
                "reward": 0,
                "rr": 0,
                "valid": False,
                "reasons": ["Invalid risk or no valid target found."]
            }

        reward = abs(tp1 - entry_price)
        rr = reward / risk

        # ----- 4. اعتبارسنجی -----
        valid = rr >= self.min_rr
        reasons = []
        if not valid:
            reasons.append(f"Risk/Reward ({rr:.2f}) is below minimum ({self.min_rr})")
        if risk < 0.2 * atr:
            reasons.append("Stop Loss too tight (volatility risk)")
        if reward < 0.4 * atr:
            reasons.append("Target too close (noise risk)")

        return {
            "entry": entry_price,
            "stop_loss": stop_loss,
            "targets": targets,
            "risk": risk,
            "reward": reward,
            "rr": rr,
            "valid": valid,
            "reasons": reasons
        }

    def _calculate_stop_loss(self, side, entry, atr,
                             swing_lows, swing_highs,
                             bullish_ob, bearish_ob,
                             support_50, resistance_50,
                             sr, poc):
        """تعیین SL بر اساس اولویت‌های Smart Money"""
        if side == "buy":
            # 1. زیر آخرین Swing Low
            if swing_lows:
                sl = min(swing_lows[-1] * 0.995, entry - atr * 1.2)
                return sl
            # 2. زیر Order Block صعودی
            if bullish_ob and isinstance(bullish_ob, dict):
                sl = bullish_ob.get("low", entry - atr * 1.5)
                return sl
            # 3. زیر Support معتبر
            if sr.get("valid_support"):
                sl = sr.get("support_level", entry - atr * 1.5)
                return sl
            # 4. ATR fallback
            return entry - atr * 1.5
        else:  # sell
            if swing_highs:
                sl = max(swing_highs[-1] * 1.005, entry + atr * 1.2)
                return sl
            if bearish_ob and isinstance(bearish_ob, dict):
                sl = bearish_ob.get("high", entry + atr * 1.5)
                return sl
            if sr.get("valid_resistance"):
                sl = sr.get("resistance_level", entry + atr * 1.5)
                return sl
            return entry + atr * 1.5

    def _calculate_targets(self, side, entry, atr,
                           swing_highs, swing_lows,
                           resistance_50, support_50,
                           bullish_ob, bearish_ob,
                           fvg, vwap, poc, fib_levels):
        """محاسبهٔ اهداف چندگانه بر اساس تحلیل تکنیکال"""
        targets = []

        if side == "buy":
            # لیست مقاومت‌های بالقوه
            resistances = []
            if swing_highs:
                resistances.extend([h for h in swing_highs if h > entry])
            if resistance_50 > entry:
                resistances.append(resistance_50)
            if bearish_ob and isinstance(bearish_ob, dict):
                resistances.append(bearish_ob.get("high", 0))
            if fvg and isinstance(fvg, dict):
                if fvg.get("bearish_fvg"):
                    resistances.append(fvg["active_fvg"]["gap_high"])
            if vwap and vwap > entry:
                resistances.append(vwap)
            if poc and poc > entry:
                resistances.append(poc)
            # فیبوناچی اکستنشن
            for level in ["0.618", "0.786", "1.0", "1.272", "1.618"]:
                if level in fib_levels and fib_levels[level] > entry:
                    resistances.append(fib_levels[level])

            # مرتب‌سازی و انتخاب ۳ هدف
            resistances = sorted(set(resistances))
            for i, r in enumerate(resistances[:3]):
                targets.append({
                    "price": round(r, 4),
                    "pct": round((r / entry - 1) * 100, 2),
                    "rr": round((r - entry) / (entry - self._calculate_stop_loss(
                        side, entry, atr, swing_lows, swing_highs, bullish_ob, bearish_ob,
                        support_50, resistance_50, {}, poc)), 2),
                    "label": f"TP{i+1}"
                })
        else:  # sell
            supports = []
            if swing_lows:
                supports.extend([l for l in swing_lows if l < entry])
            if support_50 < entry:
                supports.append(support_50)
            if bullish_ob and isinstance(bullish_ob, dict):
                supports.append(bullish_ob.get("low", 0))
            if fvg and isinstance(fvg, dict):
                if fvg.get("bullish_fvg"):
                    supports.append(fvg["active_fvg"]["gap_low"])
            if vwap and vwap < entry:
                supports.append(vwap)
            if poc and poc < entry:
                supports.append(poc)
            for level in ["0.618", "0.786", "1.0", "1.272", "1.618"]:
                if level in fib_levels and fib_levels[level] < entry:
                    supports.append(fib_levels[level])

            supports = sorted(set(supports), reverse=True)
            for i, s in enumerate(supports[:3]):
                targets.append({
                    "price": round(s, 4),
                    "pct": round((entry / s - 1) * 100, 2),
                    "rr": round((entry - s) / (self._calculate_stop_loss(
                        side, entry, atr, swing_lows, swing_highs, bullish_ob, bearish_ob,
                        support_50, resistance_50, {}, poc) - entry), 2),
                    "label": f"TP{i+1}"
                })

        # اگر هیچ هدفی یافت نشد، از ATR استفاده کن
        if not targets:
            if side == "buy":
                targets.append({
                    "price": round(entry + atr * 2, 4),
                    "pct": round(atr / entry * 2 * 100, 2),
                    "rr": 2.0,
                    "label": "TP1 (ATR-based)"
                })
            else:
                targets.append({
                    "price": round(entry - atr * 2, 4),
                    "pct": round(atr / entry * 2 * 100, 2),
                    "rr": 2.0,
                    "label": "TP1 (ATR-based)"
                })

        return targets
