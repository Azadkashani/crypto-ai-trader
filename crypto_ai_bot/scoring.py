"""
Crypto AI Bot v5.6
Advanced Scoring Engine (Professional Calibration)
"""

from config import BUY_SCORE, WATCH_SCORE


class ScoringEngine:

    @staticmethod
    def calculate(df, mtf_signal="Neutral", market_structure=None, strength="Medium"):
        last = df.iloc[-1]

        # ==================== محاسبه Score ====================
        score = 0.0
        confirmations = []   # برای Confidence (نام, مقدار امتیاز)

        struct_trend = market_structure.get("trend", "sideways") if market_structure else "sideways"
        bos = market_structure.get("bos", []) if market_structure else []
        choch = market_structure.get("choch", []) if market_structure else []
        swing_highs = market_structure.get("swing_highs", []) if market_structure else []
        swing_lows = market_structure.get("swing_lows", []) if market_structure else []
        last_event = market_structure.get("last_event", None) if market_structure else None

        last_bos = bos[-1] if bos else None
        # Opposing CHoCH فقط اگر آخرین رویداد یک CHoCH خلاف روند باشد
        opposing_choch = False
        if last_event and last_event["event"] == "choch":
            if (struct_trend == "bullish" and last_event["type"] == "bearish") or \
               (struct_trend == "bearish" and last_event["type"] == "bullish"):
                opposing_choch = True

        # 1. Market Structure
        if struct_trend == "bullish":
            score += 7
        elif struct_trend == "bearish":
            score -= 7

        if last_bos:
            if last_bos["type"] == "bullish":
                score += 12
                confirmations.append(("BOS Bullish Break", 20))
            else:
                score -= 12

        # HH/HL pattern
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-2]["label"] == "HH" and swing_lows[-2]["label"] == "HL":
                if struct_trend == "bullish":
                    score += 6
                    confirmations.append(("HH+HL Structure", 10))

        # 2. Multi Timeframe
        mtf_delta = 0
        if mtf_signal == "Strong Bullish":
            mtf_delta = 15
            confirmations.append(("MTF Strong Bullish", 15))
        elif mtf_signal == "Bullish":
            mtf_delta = 10
            confirmations.append(("MTF Bullish", 10))
        elif mtf_signal == "Bearish":
            mtf_delta = -10
        elif mtf_signal == "Strong Bearish":
            mtf_delta = -15
        score += mtf_delta

        # Alignment MTF
        if (struct_trend == "bullish" and "Bullish" in mtf_signal) or \
           (struct_trend == "bearish" and "Bearish" in mtf_signal):
            score += 4
            confirmations.append(("MTF Alignment", 10))

        # 3. EMA
        ema_score = 0
        if last["EMA20"] > last["EMA50"]:
            ema_score += 8
        if last["EMA50"] > last["EMA200"]:
            ema_score += 8
        score += ema_score
        if ema_score == 16:
            confirmations.append(("EMA Alignment", 8))

        # 4. ADX & DI
        if last["ADX"] >= 25:
            score += 8
            confirmations.append(("Strong ADX", 8))
        if last["+DI"] > last["-DI"]:
            score += 5
        elif last["-DI"] > last["+DI"]:
            score -= 5

        # 5. RSI
        rsi = last["RSI"]
        if 45 <= rsi <= 65:
            score += 8
            confirmations.append(("Healthy RSI", 5))
        elif 65 < rsi <= 75 and last["ADX"] >= 25:
            score += 6

        # 6. MACD
        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 8
            confirmations.append(("Bullish MACD", 5))

        # 7. Volume
        if last["volume"] > last["AVG_VOLUME"]:
            score += 8
            confirmations.append(("High Volume", 10))

        # 8. Volume Breakout
        resistance_20 = df["high"].tail(20).max()
        if last["close"] > resistance_20 and last["volume"] > 1.2 * last["AVG_VOLUME"]:
            score += 8
            confirmations.append(("Volume Breakout", 5))

        # 9. Location Penalty (فقط زیر ۲٪)
        distance_pct = (resistance_20 - last["close"]) / last["close"] * 100 if last["close"] > 0 else 100
        location_penalty = 0
        if distance_pct < 2.0:
            location_penalty = 5
            score -= location_penalty

        # 10. Opposing CHoCH Penalty
        choch_penalty = 0
        if opposing_choch:
            choch_penalty = 8
            score -= choch_penalty

        base_score = score

        # Strength Factor
        if strength == "Weak":
            score *= 0.8
        elif strength == "Medium":
            score *= 0.9
        # Very Strong بدون تغییر

        score = max(0, min(100, score))

        # ==================== محاسبه Confidence ====================
        # مجموع تأییدیه‌ها
        conf_confirm = sum(c[1] for c in confirmations) if confirmations else 0
        # جریمه‌ها
        conf_penalty = 0
        if location_penalty:
            conf_penalty += 5
        if opposing_choch:
            conf_penalty += 20
        if strength == "Weak":
            conf_penalty += 15
        elif strength == "Medium":
            conf_penalty += 5
        if last["ADX"] < 15:
            conf_penalty += 10

        raw_conf = 30 + conf_confirm - conf_penalty
        confidence = (raw_conf + score) / 2   # ترکیب با Score
        confidence = max(10, min(90, confidence))

        # ==================== Reasons و Warnings ====================
        reasons = []
        warnings = []

        # اولویت‌بندی دلایل: Market Structure, BOS, MTF, EMA, ADX, Volume, RSI, MACD
        if struct_trend == "bullish":
            reasons.append("Market Structure Bullish")
        elif struct_trend == "bearish":
            warnings.append("Market Structure Bearish")

        if last_bos:
            if last_bos["type"] == "bullish":
                reasons.append("BOS Bullish Break")
            else:
                warnings.append("BOS Bearish Break")

        if opposing_choch:
            warnings.append("Opposing CHoCH (active)")

        if "Bullish" in mtf_signal:
            reasons.append(f"MTF {mtf_signal}")
        elif "Bearish" in mtf_signal:
            warnings.append(f"MTF {mtf_signal}")

        if last["EMA20"] > last["EMA50"]:
            reasons.append("EMA20 > EMA50")
        if last["EMA50"] > last["EMA200"]:
            reasons.append("EMA50 > EMA200")

        if last["ADX"] >= 25:
            reasons.append("Strong ADX")
        elif last["ADX"] < 15:
            warnings.append("Weak ADX")

        if 45 <= rsi <= 65:
            reasons.append("Healthy RSI")
        elif rsi > 75:
            warnings.append("Overbought RSI")

        if last["MACD"] > last["MACD_SIGNAL"]:
            reasons.append("Bullish MACD")

        if last["volume"] > last["AVG_VOLUME"]:
            reasons.append("High Volume")
        else:
            warnings.append("Low Volume")

        if location_penalty:
            warnings.append(f"Price Near Resistance ({distance_pct:.1f}%)")

        # محدود به ۵ دلیل
        reasons = reasons[:5]

        # حذف هشدارهای تکراری یا کم‌اهمیت
        if "Low Volume" in warnings and "High Volume" in reasons:
            warnings.remove("Low Volume")
        if "Opposing CHoCH (active)" in warnings and not opposing_choch:
            warnings.remove("Opposing CHoCH (active)")

        return {
            "base_score": int(base_score),
            "mtf_bonus": int(mtf_delta),
            "score": int(round(score)),
            "confidence": int(round(confidence)),
            "breakout": last["close"] > resistance_20 and last["volume"] > 1.2 * last["AVG_VOLUME"],
            "reasons": reasons,
            "warnings": warnings
        }

    @staticmethod
    def action(score, breakout=False):
        if breakout and score >= WATCH_SCORE:
            return "BUY BREAKOUT"
        if score >= BUY_SCORE:
            return "BUY"
        if score >= WATCH_SCORE:
            return "WATCH"
        return "NO TRADE"
