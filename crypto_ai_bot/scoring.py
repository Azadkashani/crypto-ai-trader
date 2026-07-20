"""
Crypto AI Bot v5.2
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
        # EMA Trend
        # =====================================================

        if last["EMA20"] > last["EMA50"]:

            score += 20
            confidence += 15

            reasons.append("EMA Bullish")

        else:

            score -= 10
            warnings.append("EMA Weak")


        if last["EMA50"] > last["EMA200"]:

            score += 20
            confidence += 15

            reasons.append("Long Trend Bullish")

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
            reasons.append("Oversold")


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

            reasons.append("High Volume")


        # =====================================================
        # Support / Resistance Filter
        # =====================================================

        resistance_distance = (
            (resistance - price) / price
        ) * 100


        support_distance = (
            (price - support) / price
        ) * 100


        # نزدیک مقاومت
        if resistance_distance < 0.5:

            score -= 15
            warnings.append("Near Resistance")


        # نزدیک حمایت
        if support_distance < 1:

            score += 10
            reasons.append("Near Support")


        # =====================================================
        # Conflict Detection
        # =====================================================

        if (
            last["EMA20"] < last["EMA50"]
            and
            last["MACD"] > last["MACD_SIGNAL"]
        ):

            confidence -= 15
            warnings.append("Trend Conflict")


        # محدود کردن مقادیر

        score = max(0, min(score, 100))

        confidence = max(0, min(confidence, 100))


        return {

            "score": score,

            "confidence": confidence,

            "reasons": reasons,

            "warnings": warnings

        }


    @staticmethod
    def action(score):

        if score >= BUY_SCORE:

            return "BUY"


        if score >= WATCH_SCORE:

            return "WATCH"


        return "NO TRADE"
