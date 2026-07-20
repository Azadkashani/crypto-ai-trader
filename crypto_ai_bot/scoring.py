"""
Crypto AI Bot v5.5
Advanced Scoring Engine
"""

from config import BUY_SCORE, WATCH_SCORE


class ScoringEngine:


    @staticmethod
    def calculate(df, mtf_signal="Neutral"):

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

            reasons.append(
                "EMA20 > EMA50"
            )


        if last["EMA50"] > last["EMA200"]:

            score += 15
            confidence += 15

            reasons.append(
                "EMA50 > EMA200"
            )


        # ==========================
        # ADX Trend Strength
        # ==========================

        if last["ADX"] >= 25:

            score += 15
            confidence += 15

            reasons.append(
                "Strong ADX Trend"
            )

        elif last["ADX"] < 15:

            warnings.append(
                "Weak Trend"
            )


        # ==========================
        # DI Direction
        # ==========================

        if last["+DI"] > last["-DI"]:

            score += 10
            confidence += 10

            reasons.append(
                "+DI > -DI"
            )

        elif last["-DI"] > last["+DI"]:

            score -= 5

            warnings.append(
                "Bearish DI"
            )


        # ==========================
        # RSI
        # ==========================

        rsi = last["RSI"]


        if 45 <= rsi <= 65:

            score += 15
            confidence += 15

            reasons.append(
                "Healthy RSI"
            )


        elif 65 < rsi <= 75:

            if last["ADX"] >= 25:

                score += 10

                reasons.append(
                    "Strong Momentum RSI"
                )

            else:

                warnings.append(
                    "High RSI"
                )


        elif rsi < 30:

            score += 5

            reasons.append(
                "Oversold RSI"
            )


        elif rsi > 75:

            warnings.append(
                "Overbought RSI"
            )


        # ==========================
        # MACD
        # ==========================

        if last["MACD"] > last["MACD_SIGNAL"]:

            score += 15
            confidence += 15

            reasons.append(
                "Bullish MACD"
            )


        # ==========================
        # Volume Confirmation
        # ==========================

        if last["volume"] > last["AVG_VOLUME"]:

            score += 15
            confidence += 15

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


        if (
            last["close"] > resistance
            and last["volume"] > last["AVG_VOLUME"]
        ):

            breakout = True

            score += 10

            reasons.append(
                "Volume Breakout"
            )

        # ==========================
        # Multi Timeframe Confirmation
        # ==========================

        if mtf_signal == "Strong Bullish":

            score += 15
            confidence += 15

            reasons.append(
                "Strong Multi Timeframe"
            )

        elif mtf_signal == "Bullish":

            score += 8
            confidence += 8

            reasons.append(
                "Bullish Multi Timeframe"
            )

        elif mtf_signal == "Bearish":

            score -= 10
            confidence -= 10

            warnings.append(
                "Bearish Multi Timeframe"
            )

        elif mtf_signal == "Strong Bearish":

            score -= 20
            confidence -= 20

            warnings.append(
                "Strong Bearish Multi Timeframe"
            )
        
                # محدود کردن امتیاز

        score = max(0, min(score, 100))

        confidence = max(
            0,
            min(confidence, 100)
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

        if breakout and score >= WATCH_SCORE:

            return "BUY BREAKOUT"


        if score >= BUY_SCORE:

            return "BUY"


        if score >= WATCH_SCORE:

            return "WATCH"


        return "NO TRADE"
