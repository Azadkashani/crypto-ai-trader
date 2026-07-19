"""
Crypto AI Bot v5.1
Trend Engine
"""


class TrendEngine:

    @staticmethod
    def detect(df):

        last = df.iloc[-1]

        ema20 = last["EMA20"]
        ema50 = last["EMA50"]
        ema200 = last["EMA200"]

        if ema20 > ema50 > ema200:
            return "Bullish"

        elif ema20 < ema50 < ema200:
            return "Bearish"

        return "Sideways"

    @staticmethod
    def strength(df):

        last = df.iloc[-1]

        distance = abs(last["EMA20"] - last["EMA50"])

        atr = last["ATR"]

        if atr <= 0:
            return "Weak"

        ratio = distance / atr

        if ratio >= 2:
            return "Very Strong"

        elif ratio >= 1:
            return "Strong"

        elif ratio >= 0.5:
            return "Medium"

        return "Weak"

    @staticmethod
    def confidence(df):

        last = df.iloc[-1]

        score = 0

        # EMA Alignment
        if last["EMA20"] > last["EMA50"]:
            score += 25

        if last["EMA50"] > last["EMA200"]:
            score += 25

        # RSI
        if 45 <= last["RSI"] <= 70:
            score += 20

        # MACD
        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 20

        # Volume
        volume_mean = df["volume"].tail(20).mean()

        if last["volume"] > volume_mean:
            score += 10

        return score

    @staticmethod
    def alignment(trends):

        """
        trends مثال:
        ["Bullish","Bullish","Sideways"]
        """

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
