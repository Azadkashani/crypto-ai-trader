"""
Crypto AI Bot v5.6
Advanced Scoring Engine (Balanced)
"""

from config import BUY_SCORE, WATCH_SCORE


class ScoringEngine:

    @staticmethod
    def calculate(df, mtf_signal="Neutral", market_structure=None, strength="Medium"):
        last = df.iloc[-1]

        # ==================== محاسبه Score ====================
        score = 0.0

        struct_trend = market_structure.get("trend", "sideways") if market_structure else "sideways"
        bos = market_structure.get("bos", []) if market_structure else []
        choch = market_structure.get("choch", []) if market_structure else []
        swing_highs = market_structure.get("swing_highs", []) if market_structure else []
        swing_lows = market_structure.get("swing_lows", []) if market_structure else []

        last_bos = bos[-1] if bos else None
        last_choch = choch[-1] if choch else None

        # 1. Market Structure
        if struct_trend == "bullish":
            score += 3
        elif struct_trend == "bearish":
            score -= 3

        if last_bos:
            if last_bos["type"] == "bullish":
                score += 8
            else:
                score -= 8

        # HH/HL pattern
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-2]["label"] == "HH" and swing_lows[-2]["label"] == "HL":
                if struct_trend == "bullish":
                    score += 4
            elif swing_highs[-2]["label"] == "LH" and swing_lows[-2]["label"] == "LL":
                if struct_trend == "bearish":
                    score -= 4

        # 2. Multi Timeframe
        mtf_delta = 0
        if mtf_signal == "Strong Bullish":
            mtf_delta = 8
        elif mtf_signal == "Bullish":
            mtf_delta = 4
        elif mtf_signal == "Bearish":
            mtf_delta = -4
        elif mtf_signal == "Strong Bearish":
            mtf_delta = -8
        score += mtf_delta

        if (struct_trend == "bullish" and "Bullish" in mtf_signal) or \
           (struct_trend == "bearish" and "Bearish" in mtf_signal):
            score += 2

        # 3. EMA
        if last["EMA20"] > last["EMA50"]:
            score += 5
        if last["EMA50"] > last["EMA200"]:
            score += 5

        # 4. ADX & DI
        if last["ADX"] >= 25:
            score += 5
        if last["+DI"] > last["-DI"]:
            score += 3
        elif last["-DI"] > last["+DI"]:
            score -= 3

        # 5. RSI
        rsi = last["RSI"]
        if 45 <= rsi <= 65:
            score += 5
        elif 65 < rsi <= 75 and last["ADX"] >= 25:
            score += 3

        # 6. MACD
        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 5

        # 7. Volume
        if last["volume"] > last["AVG_VOLUME"]:
            score += 5

        # 8. Volume Breakout
        resistance_20 = df["high"].tail(20).max()
        if last["close"] > resistance_20 and last["volume"] > 1.2 * last["AVG_VOLUME"]:
            score += 5

        # 9. Location Penalty (کاهش یافته)
        atr_val = last["ATR"] if last["ATR"] > 0 else 0.0001
        distance_to_res = (resistance_20 - last["close"]) / atr_val
        location_penalty = 0
        if distance_to_res < 2.0:
            location_penalty = 5
            score -= location_penalty

        # 10. CHoCH Penalty (کاهش یافته)
        choch_penalty = 0
        if last_choch:
            if (struct_trend == "bullish" and last_choch["type"] == "bearish") or \
               (struct_trend == "bearish" and last_choch["type"] == "bullish"):
                choch_penalty = 3
                score -= choch_penalty

        # ذخیره Base Score
        base_score = score

        # Strength Factor (نرم‌تر)
        if strength == "Weak":
            score *= 0.8
        elif strength == "Medium":
            score *= 0.9
        # Very Strong: بدون تغییر

        # محدودسازی Score
        score = max(0, min(100, score))

        # ==================== محاسبه Confidence ====================
        conf = 30.0

        if last_bos:
            conf += 20
        if (struct_trend == "bullish" and "Bullish" in mtf_signal) or \
           (struct_trend == "bearish" and "Bearish" in mtf_signal):
            conf += 15
        if last["volume"] > last["AVG_VOLUME"]:
            conf += 10
        if strength in ("Strong", "Very Strong"):
            conf += 10
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            if swing_highs[-2]["label"] == "HH" and swing_lows[-2]["label"] == "HL":
                conf += 10

        # Penalties
        if last_choch and ((struct_trend == "bullish" and last_choch["type"] == "bearish") or
                           (struct_trend == "bearish" and last_choch["type"] == "bullish")):
            conf -= 15
        if location_penalty:
            conf -= 5

        conf = max(10, min(90, conf))

        # ==================== Reasons و Warnings ====================
        reasons = []
        warnings = []

        if struct_trend == "bullish":
            reasons.append("Market Structure Bullish")
        elif struct_trend == "bearish":
            warnings.append("Market Structure Bearish")

        if last_bos:
            if last_bos["type"] == "bullish":
                reasons.append("BOS Bullish Break")
            else:
                warnings.append("BOS Bearish Break")

        if last_choch:
            if (struct_trend == "bullish" and last_choch["type"] == "bearish") or \
               (struct_trend == "bearish" and last_choch["type"] == "bullish"):
                warnings.append("Opposing CHoCH")

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
            warnings.append("Price Near Resistance")

        reasons = reasons[:5]
        warnings.sort(key=lambda w: "CHoCH" in w, reverse=True)

        return {
            "base_score": int(base_score),
            "mtf_bonus": int(mtf_delta),
            "score": int(round(score)),
            "confidence": int(round(conf)),
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
