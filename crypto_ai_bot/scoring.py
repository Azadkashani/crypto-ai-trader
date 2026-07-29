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
        # EMA Trend
        # ==========================
        if last["EMA20"] > last["EMA50"]:
            score += 15
            confidence += 15
            reasons.append("EMA20 > EMA50")

        if last["EMA50"] > last["EMA200"]:
            score += 15
            confidence += 15
            reasons.append("EMA50 > EMA200")

        # ==========================
        # ADX Trend Strength
        # ==========================
        if last["ADX"] >= 25:
            score += 15
            confidence += 15
            reasons.append("Strong ADX Trend")
        elif last["ADX"] < 15:
            warnings.append("Weak Trend")

        # ==========================
        # DI Direction
        # ==========================
        if last["+DI"] > last["-DI"]:
            score += 10
            confidence += 10
            reasons.append("+DI > -DI")
        elif last["-DI"] > last["+DI"]:
            score -= 5
            warnings.append("Bearish DI")

        # ==========================
        # RSI
        # ==========================
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

        # ==========================
        # MACD
        # ==========================
        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 15
            confidence += 15
            reasons.append("Bullish MACD")

        # ==========================
        # Volume Confirmation
        # ==========================
        if last["volume"] > last["AVG_VOLUME"]:
            score += 15
            confidence += 15
            reasons.append("High Volume")

        # ==========================
        # Breakout Detection
        # ==========================
        resistance = df["high"].tail(50).max()
        if last["close"] > resistance and last["volume"] > last["AVG_VOLUME"]:
            breakout = True
            score += 10
            reasons.append("Volume Breakout")

        # ==========================
        # Market Structure Integration
        # ==========================
        if market_structure is not None:
            struct_trend = market_structure.get("trend", "sideways")
            swing_highs = market_structure.get("swing_highs", [])
            swing_lows = market_structure.get("swing_lows", [])
            bos = market_structure.get("bos", [])
            choch = market_structure.get("choch", [])

            # 1) روند ساختاری (فقط بر اساس BOS)
            if struct_trend == "bullish":
                score += 15
                confidence += 15
                reasons.append("Market Structure Bullish")
            elif struct_trend == "bearish":
                score -= 15
                confidence -= 15
                warnings.append("Market Structure Bearish")

            # 2) الگوی HH/HL یا LH/LL (تأیید ساختار)
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                last_hh_label = swing_highs[-2]["label"]
                last_ll_label = swing_lows[-2]["label"]
                if struct_trend == "bullish" and last_hh_label == "HH" and last_ll_label == "HL":
                    score += 5
                    confidence += 5
                    reasons.append("Strong HH+HL Structure")
                elif struct_trend == "bearish" and last_hh_label == "LH" and last_ll_label == "LL":
                    score -= 5
                    confidence -= 5
                    warnings.append("Strong LH+LL Structure")

            # 3) آخرین رویداد BOS / CHoCH (فقط یکی)
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
                        score += 3
                        confidence += 2
                        reasons.append("CHoCH Bullish (Potential Reversal)")
                    else:  # bearish
                        score -= 3
                        confidence -= 2
                        warnings.append("CHoCH Bearish (Potential Reversal)")
                else:  # bos
                    if last_event["type"] == "bullish":
                        score += 10
                        confidence += 10
                        reasons.append("BOS Bullish Break")
                    else:
                        score -= 10
                        confidence -= 10
                        warnings.append("BOS Bearish Break")

        # ==========================
        # Base Score (تا اینجا)
        # ==========================
        base_score = score

        # ==========================
        # Multi Timeframe Confirmation
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

        # محدود کردن امتیاز
        score = max(0, min(score, 100))
        confidence = max(0, min(confidence, 100))

        return {
            "base_score": base_score,
            "mtf_bonus": mtf_delta,
            "score": score,
            "confidence": confidence,
            "breakout": breakout,
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
