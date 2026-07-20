"""
Crypto AI Bot v5.4
Scoring Engine
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

        breakout = False


        # ==========================
        # EMA Trend
        # ==========================

        if last["EMA20"] > last["EMA50"]:

            score += 20

            confidence += 20

            reasons.append(
                "EMA20 > EMA50"
            )


        if last["EMA50"] > last["EMA200"]:

            score += 20

            confidence += 20

            reasons.append(
                "EMA50 > EMA200"
            )


        # ==========================
        # RSI
        # ==========================

        rsi = last["RSI"]


        if 40 <= rsi <= 65:

            score += 20

            confidence += 20

            reasons.append(
                "Healthy RSI"
            )


        elif rsi > 70:

            warnings.append(
                "Overbought RSI"
            )


        elif rsi < 30:

            score += 10

            reasons.append(
                "Oversold RSI"
            )


        # ==========================
        # MACD
        # ==========================

        if last["MACD"] > last["MACD_SIGNAL"]:

            score += 20

            confidence += 20

            reasons.append(
                "Bullish MACD"
            )


        # ==========================
        # Volume
        # ==========================

        avg_volume = (
            df["volume"]
            .tail(20)
            .mean()
        )


        if last["volume"] > avg_volume:

            score += 20

            confidence += 20

            reasons.append(
                "High Volume"
            )


        # ==========================
        # Breakout Detection
        # ==========================

        resistance = (
            df["high"]
            .tail(50)
            .max()
        )


        if last["close"] > resistance:

            breakout = True

            score += 10

            reasons.append(
                "Resistance Breakout"
            )


        return {

            "score": min(score,100),

            "confidence": min(confidence,100),

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
