"""
Crypto AI Bot v4
Trend Engine
"""


class TrendEngine:

    @staticmethod
    def detect(df):

        last = df.iloc[-1]

        ema20 = last["EMA20"]
        ema50 = last["EMA50"]
        ema200 = last["EMA200"]

        # Strong Bullish
        if ema20 > ema50 > ema200:
            return "Bullish"

        # Strong Bearish
        if ema20 < ema50 < ema200:
            return "Bearish"

        # Neutral
        return "Sideways"

    @staticmethod
    def strength(df):

        last = df.iloc[-1]

        distance = abs(last["EMA20"] - last["EMA50"])

        atr = last["ATR"]

        if atr == 0:
            return "Weak"

        ratio = distance / atr

        if ratio >= 2:
            return "Very Strong"

        if ratio >= 1:
            return "Strong"

        if ratio >= 0.5:
            return "Medium"

        return "Weak"
