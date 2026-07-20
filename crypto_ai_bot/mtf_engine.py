"""
Crypto AI Bot v5.7
Multi Timeframe Engine
"""


from indicators import IndicatorEngine
from trend import TrendEngine



class MTFEngine:



    @staticmethod
    def analyze(timeframes):


        results = {}


        for tf, df in timeframes.items():


            df = IndicatorEngine.calculate(df)


            trend = TrendEngine.detect(df)


            results[tf] = trend



        score = 0


        if results.get("15m") == "Bullish":

            score += 40

        elif results.get("15m") == "Bearish":

            score -= 40



        if results.get("1h") == "Bullish":

            score += 30

        elif results.get("1h") == "Bearish":

            score -= 30



        if results.get("4h") == "Bullish":

            score += 30

        elif results.get("4h") == "Bearish":

            score -= 30



        if score >= 80:

            alignment = "Strong Bullish"


        elif score >= 40:

            alignment = "Bullish"


        elif score <= -80:

            alignment = "Strong Bearish"


        elif score <= -40:

            alignment = "Bearish"


        else:

            alignment = "Neutral"



        return {

            "score": score,

            "alignment": alignment,

            "trends": results

        }
