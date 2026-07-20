"""
Crypto AI Bot v5.4
Signal Quality Scoring Engine
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


        # ===============================
        # Trend Detection
        # ===============================

        bullish_trend = False

        if last["EMA20"] > last["EMA50"]:

            score += 20
            reasons.append("EMA Short Bullish")

        else:

            score -= 10
            warnings.append("EMA Weak")


        if last["EMA50"] > last["EMA200"]:

            score += 20
            bullish_trend = True
            reasons.append("EMA Long Bullish")

        else:

            score -= 10
            warnings.append("Long Trend Bearish")


        # ===============================
        # RSI Filter
        # ===============================

        rsi = last["RSI"]


        if 45 <= rsi < 70:

            score += 15
            confidence += 15
            reasons.append("Healthy RSI")


        elif rsi >= 70:

            score -= 10
            warnings.append("RSI Overbought")


        elif rsi < 30:

            score += 10
            reasons.append("Oversold RSI")



        # ===============================
        # MACD
        # ===============================

        macd_bullish = False


        if last["MACD"] > last["MACD_SIGNAL"]:

            score += 15
            macd_bullish = True
            reasons.append("MACD Bullish")

        else:

            score -= 10
            warnings.append("MACD Bearish")



        # ===============================
        # Volume
        # ===============================

        avg_volume = df["volume"].tail(20).mean()


        if last["volume"] > avg_volume:

            score += 10
            confidence += 10
            reasons.append("Volume Confirmed")



        # ===============================
        # Support / Resistance
        # ===============================

        resistance_distance = (
            (resistance - price) / price
        ) * 100


        support_distance = (
            (price - support) / price
        ) * 100



        breakout = False


        if price > resistance:

            breakout = True

            score += 15
            confidence += 20

            reasons.append(
                "Resistance Breakout"
            )


        elif resistance_distance < 0.3:

            score -= 15

            warnings.append(
                "Near Resistance"
            )


        if support_distance < 1:

            score += 5

            reasons.append(
                "Near Support"
            )



        # ===============================
        # Final Quality Filter
        # ===============================


        # بدون روند مشخص BUY ممنوع
        if not bullish_trend:

            if score >= BUY_SCORE:

                score = WATCH_SCORE

            warnings.append(
                "No Strong Trend"
            )


        # تضاد MACD و روند

        if bullish_trend and not macd_bullish:

            confidence -= 15

            warnings.append(
                "MACD Conflict"
            )



        score = max(
            0,
            min(score,100)
        )


        confidence = max(
            0,
            min(confidence,100)
        )


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
