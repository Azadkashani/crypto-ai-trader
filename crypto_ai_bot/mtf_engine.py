"""
Crypto AI Bot v5.7
Multi Timeframe Engine
"""


from timeframe import (
    TIMEFRAME_WEIGHT
)


class MTFEngine:


    @staticmethod
    def analyze(results):

        """
        Example:

        {
            "15m": "Bullish",
            "1h": "Bullish",
            "4h": "Bearish"
        }

        """

        bullish_score = 0
        bearish_score = 0


        details = {}



        for tf, trend in results.items():


            weight = TIMEFRAME_WEIGHT.get(tf, 0)


            details[tf] = trend


            if trend == "Bullish":

                bullish_score += weight


            elif trend == "Bearish":

                bearish_score += weight



        net_score = round(
            (bullish_score - bearish_score) * 100,
            2
        )



        if bullish_score >= 0.7:

            signal = "Strong Bullish"


        elif bearish_score >= 0.7:

            signal = "Strong Bearish"


        elif bullish_score > bearish_score:

            signal = "Bullish"


        elif bearish_score > bullish_score:

            signal = "Bearish"


        else:

            signal = "Neutral"



        return {

            "signal": signal,

            "bullish": round(
                bullish_score * 100,
                2
            ),

            "bearish": round(
                bearish_score * 100,
                2
            ),

            "score": net_score,

            "details": details

        }
