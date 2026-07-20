"""
Crypto AI Bot v5.6
Multi Timeframe Engine
"""

from timeframe import TIMEFRAME_WEIGHT


class MTFEngine:

    @staticmethod
    def analyze(results):
        """
        results example:

        {
            "15m": "Bullish",
            "1h": "Bullish",
            "4h": "Bearish"
        }
        """

        bullish = 0.0
        bearish = 0.0

        for tf, trend in results.items():

            weight = TIMEFRAME_WEIGHT.get(tf, 0)

            if trend == "Bullish":
                bullish += weight

            elif trend == "Bearish":
                bearish += weight

        if bullish >= 0.7:
            return "Strong Bullish"

        elif bearish >= 0.7:
            return "Strong Bearish"

        elif bullish > bearish:
            return "Bullish"

        elif bearish > bullish:
            return "Bearish"

        return "Neutral"
