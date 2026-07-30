"""
Crypto AI Bot
Trade Analyzer: Smart Summaries, Entry Quality, Trade Readiness
"""

from weights import REASON_WEIGHTS, WARNING_WEIGHTS


class TradeAnalyzer:

    @staticmethod
    def market_bias(trend, strength):
        if trend == "Bullish":
            if strength in ("Very Strong", "Strong"):
                return "Strong Bullish"
            else:
                return "Bullish"
        elif trend == "Bearish":
            if strength in ("Very Strong", "Strong"):
                return "Strong Bearish"
            else:
                return "Bearish"
        else:
            return "Sideways"

    @staticmethod
    def generate_summary(action, trend, strength, warnings, reasons, confidence):
        bias = TradeAnalyzer.market_bias(trend, strength)
        # Why not Buy? (if action is not BUY)
        why_not = []
        if action not in ("BUY", "STRONG BUY"):
            # collect top 3 warnings
            sorted_w = sorted(warnings, key=lambda w: WARNING_WEIGHTS.get(w, 0), reverse=True)
            why_not = sorted_w[:3]
        # Current Status
        if action in ("BUY", "STRONG BUY"):
            status = "Ready for entry"
        elif action == "WATCH":
            status = "Waiting for confirmation"
        else:
            status = "No trade"
        # Next Trigger
        next_trigger = ""
        if action == "WATCH":
            missing = []
            if "Low Volume" in warnings:
                missing.append("Volume increase")
            if any("Resistance" in w for w in warnings):
                missing.append("Break above resistance")
            if "Bearish Divergence" in " ".join(warnings):
                missing.append("Divergence cleared")
            if missing:
                next_trigger = ", ".join(missing)
            else:
                next_trigger = "Monitor for breakout"
        elif action == "BUY":
            next_trigger = "Manage risk with SL/TP"
        elif action == "STRONG BUY":
            next_trigger = "High confidence entry"
        else:
            next_trigger = "Wait for trend change"

        return {
            "Market Bias": bias,
            "Why Not Buy?": why_not,
            "Current Status": status,
            "Next Trigger": next_trigger
        }

    @staticmethod
    def entry_quality(entry, support, resistance, atr, strength, breakout, advanced_data=None):
        score = 0
        # فاصله تا مقاومت (نسبت به ATR)
        dist_res = (resistance - entry) / atr if atr > 0 else 0
        if dist_res > 3:
            score += 2
        elif dist_res > 1.5:
            score += 1

        # فاصله تا حمایت (نسبت به ATR)
        dist_sup = (entry - support) / atr if atr > 0 else 0
        if dist_sup > 2:
            score += 2
        elif dist_sup > 1:
            score += 1

        # Risk Reward (بر اساس SL/TP پیش‌فرض 1.5/3)
        rr = 2.0  # همیشه 2:1
        if rr >= 2:
            score += 2
        elif rr >= 1.5:
            score += 1

        # Strength
        if strength == "Very Strong":
            score += 3
        elif strength == "Strong":
            score += 2
        elif strength == "Medium":
            score += 1

        # Breakout
        if breakout:
            score += 3

        # Advanced factors
        if advanced_data:
            if advanced_data.get("liquidity_sweep", {}).get("buy_side_sweep"):
                score += 2
            if advanced_data.get("order_block", {}).get("valid"):
                if advanced_data["order_block"].get("bullish_ob"):
                    score += 2
            if advanced_data.get("fvg", {}).get("bullish_fvg"):
                score += 1
            if advanced_data.get("volume_profile", {}).get("distance_to_poc", 100) < 2:
                score += 1

        if score >= 12:
            return "A+"
        elif score >= 10:
            return "A"
        elif score >= 8:
            return "B+"
        elif score >= 6:
            return "B"
        elif score >= 4:
            return "C"
        else:
            return "D"

    @staticmethod
    def trade_readiness(score, confidence, trend, strength, mtf_signal, breakout, vol_ok, warnings):
        base = 0
        if trend == "Bullish":
            base += 25
        elif trend == "Bearish":
            base -= 25
        # Strength
        if strength == "Very Strong":
            base += 20
        elif strength == "Strong":
            base += 15
        elif strength == "Medium":
            base += 5
        else:
            base -= 10
        # MTF
        if "Bullish" in mtf_signal:
            base += 20
        elif "Bearish" in mtf_signal:
            base -= 15
        # Breakout
        if breakout:
            base += 15
        # Volume
        if vol_ok:
            base += 10
        # Warnings severity
        warning_penalty = 0
        for w in warnings:
            weight = WARNING_WEIGHTS.get(w, 1)
            warning_penalty += weight
        base -= warning_penalty * 2
        # Normalize 0-100
        readiness = base + 50  # shift
        readiness = max(0, min(100, readiness))
        return int(readiness)

    @staticmethod
    def watch_reason(action, trend, reasons, warnings):
        if action != "WATCH":
            return None
        lines = []
        lines.append(f"✓ Trend {trend}")
        for r in reasons[:5]:
            lines.append(f"✓ {r}")
        # نشان دادن موانع
        for w in warnings[:5]:
            lines.append(f"✗ {w}")
        return lines
