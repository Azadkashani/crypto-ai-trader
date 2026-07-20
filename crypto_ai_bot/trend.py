"""
Crypto AI Bot v5.2
Trend Engine
"""


class TrendEngine:


    @staticmethod
    def detect(df):

        last = df.iloc[-1]

        ema20 = last["EMA20"]
        ema50 = last["EMA50"]
        ema200 = last["EMA200"]

        adx = last["ADX"]


        # روند معتبر فقط وقتی ADX مناسب باشد

        if adx < 20:
            return "Sideways"


        if ema20 > ema50 > ema200:
            return "Bullish"


        elif ema20 < ema50 < ema200:
            return "Bearish"


        return "Sideways"



    @staticmethod
    def strength(df):

        last = df.iloc[-1]

        distance = abs(
            last["EMA20"] - last["EMA50"]
        )

        atr = last["ATR"]

        adx = last["ADX"]


        if atr <= 0:
            return "Weak"


        ratio = distance / atr


        # ترکیب فاصله EMA و قدرت ADX

        if adx >= 40 and ratio >= 1:
            return "Very Strong"


        elif adx >= 25 and ratio >= 0.8:
            return "Strong"


        elif adx >= 20:
            return "Medium"


        return "Weak"



    @staticmethod
    def confidence(df):

        last = df.iloc[-1]

        score = 0


        # EMA

        if last["EMA20"] > last["EMA50"]:
            score += 20


        if last["EMA50"] > last["EMA200"]:
            score += 20



        # ADX

        if last["ADX"] >= 25:
            score += 20

        elif last["ADX"] >= 20:
            score += 10



        # RSI

        if 45 <= last["RSI"] <= 70:
            score += 15



        # MACD

        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 15



        # Volume

        volume_mean = (
            df["volume"]
            .tail(20)
            .mean()
        )

        if last["volume"] > volume_mean:
            score += 10



        return min(score,100)



    @staticmethod
    def alignment(trends):

        bullish = trends.count("Bullish")

        bearish = trends.count("Bearish")


        if bullish == len(trends):
            return 100


        if bearish == len(trends):
            return 100


        if bullish == 2 or bearish == 2:
            return 66


        if bullish == 1 or bearish == 1:
            return 33


        return 0
