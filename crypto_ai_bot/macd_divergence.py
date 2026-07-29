"""
MACD Divergence
"""

class MACDDivergence:
    @staticmethod
    def detect(df):
        if len(df) < 20:
            return {"bullish_div": False, "bearish_div": False}
        df = df.copy()
        df["price_peak"] = df["high"].rolling(5, center=True).max()
        df["macd_peak"] = df["MACD_HIST"].rolling(5, center=True).max()
        last_two_price = df["price_peak"].dropna().iloc[-2:]
        last_two_macd = df["macd_peak"].dropna().iloc[-2:]
        if len(last_two_price) < 2:
            return {"bullish_div": False, "bearish_div": False}
        if last_two_price.iloc[-1] > last_two_price.iloc[-2] and last_two_macd.iloc[-1] < last_two_macd.iloc[-2]:
            return {"bullish_div": False, "bearish_div": True}
        return {"bullish_div": False, "bearish_div": False}
