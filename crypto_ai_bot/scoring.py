"""
Crypto AI Bot v5.5
Advanced Scoring Engine
"""

from config import BUY_SCORE, WATCH_SCORE


class ScoringEngine:

    @staticmethod
    def calculate(df, mtf_signal="Neutral", market_structure=None):
        last = df.iloc[-1]

        score = 0
        confidence = 0

        reasons = []
        warnings = []

        breakout = False

        # ==========================
        # بخش اول: ساختار بازار
        # ==========================
        struct_trend = "sideways"
        if market_structure is not None:
            struct_trend = market_structure.get("trend", "sideways")
            swing_highs = market_structure.get("swing_highs", [])
            swing_lows = market_structure.get("swing_lows", [])
            bos = market_structure.get("bos", [])
            choch = market_structure.get("choch", [])

            # روند ساختاری (وزن کم)
            if struct_trend == "bullish":
                score += 5
                confidence += 5
                reasons.append("Market Structure Bullish")
            elif struct_trend == "bearish":
                score -= 5
                confidence -= 5
                warnings.append("Market Structure Bearish")

            # الگوی HH/HL یا LH/LL (صرفاً توصیف)
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                last_hh_label = swing_highs[-2]["label"]
                last_ll_label = swing_lows[-2]["label"]
                if struct_trend == "bullish" and last_hh_label == "HH" and last_ll_label == "HL":
                    reasons.append("Higher High & Higher Low")
                elif struct_trend == "bearish" and last_hh_label == "LH" and last_ll_label == "LL":
                    warnings.append("Lower High & Lower Low")

            # جزئیات آخرین سقف و کف
            if swing_highs:
                label_h = swing_highs[-1]["label"]
                if struct_trend == "bullish" and label_h == "HH":
                    reasons.append("Higher High")
                elif struct_trend == "bearish" and label_h == "LH":
                    warnings.append("Lower High")
            if swing_lows:
                label_l = swing_lows[-1]["label"]
                if struct_trend == "bullish" and label_l == "HL":
                    reasons.append("Higher Low")
                elif struct_trend == "bearish" and label_l == "LL":
                    warnings.append("Lower Low")

            # آخرین رویداد BOS / CHoCH (فقط یکی)
            all_events = []
            for ev in bos:
                all_events.append({**ev, "event": "bos"})
            for ev in choch:
                all_events.append({**ev, "event": "choch"})
            if all_events:
                all_events.sort(key=lambda x: x["index"])
                last_event = all_events[-1]
                if last_event["event"] == "choch":
                    if last_event["type"] == "bullish":
                        score += 2
                        confidence += 2
                        warnings.append("CHoCH Bullish (Potential Reversal)")
                    else:
                        score -= 2
                        confidence -= 2
                        warnings.append("CHoCH Bearish (Potential Reversal)")
                else:  # bos
                    if last_event["type"] == "bullish":
                        score += 8
                        confidence += 8
                        reasons.append("BOS Bullish Break")
                    else:
                        score -= 8
                        confidence -= 8
                        warnings.append("BOS Bearish Break")

        # ==========================
        # اندیکاتورهای کلاسیک
        # ==========================
        if last["EMA20"] > last["EMA50"]:
            score += 15
            confidence += 15
            reasons.append("EMA20 > EMA50")

        if last["EMA50"] > last["EMA200"]:
            score += 15
            confidence += 15
            reasons.append("EMA50 > EMA200")

        if last["ADX"] >= 25:
            score += 15
            confidence += 15
            reasons.append("Strong ADX Trend")
        elif last["ADX"] < 15:
            warnings.append("Weak Trend")

        if last["+DI"] > last["-DI"]:
            score += 10
            confidence += 10
            reasons.append("+DI > -DI")
        elif last["-DI"] > last["+DI"]:
            score -= 5
            warnings.append("Bearish DI")

        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 15
            confidence += 15
            reasons.append("Bullish MACD")

        rsi = last["RSI"]
        if 45 <= rsi <= 65:
            score += 15
            confidence += 15
            reasons.append("Healthy RSI")
        elif 65 < rsi <= 75:
            if last["ADX"] >= 25:
                score += 10
                reasons.append("Strong Momentum RSI")
            else:
                warnings.append("High RSI")
        elif rsi < 30:
            score += 5
            reasons.append("Oversold RSI")
        elif rsi > 75:
            warnings.append("Overbought RSI")

        if last["volume"] > last["AVG_VOLUME"]:
            score += 15
            confidence += 15
            reasons.append("High Volume")

        # ==========================
        # Volume Breakout (شکست کانال)
        # ==========================
        resistance = df["high"].tail(50).max()
        if last["close"] > resistance and last["volume"] > last["AVG_VOLUME"]:
            breakout = True
            score += 10
            reasons.append("Volume Breakout")

        # ==========================
        # Base Score (تا اینجا)
        # ==========================
        base_score = score

        # ==========================
        # Multi Timeframe
        # ==========================
        mtf_delta = 0
        if mtf_signal == "Strong Bullish":
            mtf_delta = 15
            confidence += 15
            reasons.append("Strong Multi Timeframe")
        elif mtf_signal == "Bullish":
            mtf_delta = 8
            confidence += 8
            reasons.append("Bullish Multi Timeframe")
        elif mtf_signal == "Bearish":
            mtf_delta = -10
            confidence -= 10
            warnings.append("Bearish Multi Timeframe")
        elif mtf_signal == "Strong Bearish":
            mtf_delta = -20
            confidence -= 20
            warnings.append("Strong Bearish Multi Timeframe")

        score += mtf_delta

        # ==========================
        # امتیاز هم‌جهتی ساختار با MTF
        # ==========================
        if struct_trend == "bullish" and "Bullish" in mtf_signal:
            score += 5
            confidence += 5
            reasons.append("Structure & MTF Alignment")
        elif struct_trend == "bearish" and "Bearish" in mtf_signal:
            score -= 5
            confidence -= 5
            warnings.append("Structure & MTF Alignment Bearish")

        # محدودسازی
        score = max(0, min(score, 100))
        confidence = max(0, min(confidence, 100))

        return {
            "base_score": base_score,
            "mtf_bonus": mtf_delta,
            "score": score,
            "confidence": confidence,
            "breakout": breakout,          # این همان Volume Breakout است
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
