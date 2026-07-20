%%writefile mtf_engine.py

"""
Crypto AI Bot v5.7
Multi Timeframe Engine
"""


from indicators import IndicatorEngine
from trend import TrendEngine



class MTFEngine:


    @staticmethod
    def analyze(dataframes):

        results = {}

        bullish = 0
        bearish = 0


        for tf, df in dataframes.items():

            df = IndicatorEngine.calculate(df)

            trend = TrendEngine.detect(df)

            strength = TrendEngine.strength(df)


            results[tf] = {

                "trend": trend,

                "strength": strength

            }


            if trend == "Bullish":

                bullish += 1


            elif trend == "Bearish":

                bearish += 1



        total = len(dataframes)


        if bullish == total:

            final_trend = "Bullish"


        elif bearish == total:

            final_trend = "Bearish"


        else:

            final_trend = "Mixed"



        confidence = int(
            max(bullish, bearish)
            /
            total
            *
            100
        )


        return {

            "timeframes": results,

            "final_trend": final_trend,

            "confidence": confidence

        }
