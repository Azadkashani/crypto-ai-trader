"""
Crypto AI Bot v5.3
Advanced Scoring Engine
"""

from config import BUY_SCORE
from config import WATCH_SCORE


class ScoringEngine:

    @staticmethod
    def calculate(df):

        last = df.iloc[-1]

        score = 0
        confidence = 0

        reasons = []
        warnings = []

        price = last["close"]

        support = df["low"].tail(50).min()
        resistance = df["high"].tail(50).max()

        # =====================================================
        # Trend EMA
        # =====================================================

        if last["EMA20"] > last["EMA50"]:

            score += 20
            confidence += 15
            reasons.append("EMA Short Trend Bullish")

        else:

            score -= 10
            warnings.append("EMA Short Trend Weak")


        if last["EMA50"] > last["EMA200"]:

            score += 20
            confidence += 15
            reasons.append("EMA Long Trend Bullish")

        else:

            score -= 10
            warnings.append("Long Trend Bearish")


        # =====================================================
        # RSI
        # =====================================================

        rsi = last["RSI"]

        if 45 <= rsi <= 70:

            score += 15
            confidence += 15
            reasons.append("Healthy RSI")

        elif rsi < 30:

            score += 10
            reasons.append("Oversold RSI")

        elif rsi > 75:

            score -= 10
            warnings.append("Overbought")


        # =====================================================
        # MACD
        # =====================================================

        if last["MACD"] > last["MACD_SIGNAL"]:

            score += 15
            confidence += 10
            reasons.append("MACD Bullish")

        else:

            score -= 10
            warnings.append("MACD Bearish")


        # =====================================================
        # Volume
        # =====================================================

        avg_volume = df["volume"].tail(20).mean()

        if last["volume"] > avg_volume:

            score += 10
            confidence += 10
            reasons.append("Volume Confirmation")


        # =====================================================
        # Resistance / Support
        # =====================================================

        resistance_distance = (
            (resistance - price) / price
        ) * 100


        support_distance = (
            (price - support) / price
        ) * 100


        breakout = False


        # Breakout confirmed
        if price > resistance:

            breakout = True

            score += 15
            confidence += 15

            reasons.append("Resistance Breakout")


        # نزدیک مقاومت ولی شکست نداده
        elif resistance_distance < 0.3:

            score -= 15
            confidence -= 10

            warnings.append(
                "Too Close To Resistance"
            )


        # نزدیک حمایت
        if support_distance < 1:

            score += 10

            reasons.append(
                "Near Support"
            )


        # =====================================================
        # Final Adjustment
        # =====================================================

        score = max(0, min(score, 100))

        confidence = max(0, min(confidence, 100))


        return {

            "score": score,

            "confidence": confidence,

            "breakout": breakout,

            "reasons": reasons,

            "warnings": warnings

        }


    @staticmethod
    def action(score, breakout=False):

        if score >= BUY_SCORE and breakout:

            return "BUY BREAKOUT"


        if score >= BUY_SCORE:

            return "BUY"


        if score >= WATCH_SCORE:

            return "WATCH"


        return "NO TRADE"
