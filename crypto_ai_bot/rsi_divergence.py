"""
RSI Divergence (ساده: مقایسه قله‌ها)
"""

class RSIDivergence:
    @staticmethod
    def detect(df, window=5):
        if len(df) < window + 2:
            return {"bullish_divergence": False, "bearish_divergence": False}
        df = df.copy()
        df["price_high"] = df["high"].rolling(window, center=True).max()
        df["rsi_high"] = df["RSI"].rolling(window, center=True).max()
        recent_highs_price = df["price_high"].dropna().iloc[-2:]
        recent_highs_rsi = df["rsi_high"].dropna().iloc[-2:]
        if len(recent_highs_price) < 2:
            return {"bullish_divergence": False, "bearish_divergence": False}
        if recent_highs_price.iloc[-1] > recent_highs_price.iloc[-2] and \
           recent_highs_rsi.iloc[-1] < recent_highs_rsi.iloc[-2]:
            return {"bullish_divergence": False, "bearish_divergence": True}
        df["price_low"] = df["low"].rolling(window, center=True).min()
        df["rsi_low"] = df["RSI"].rolling(window, center=True).min()
        recent_lows_price = df["price_low"].dropna().iloc[-2:]
        recent_lows_rsi = df["rsi_low"].dropna().iloc[-2:]
        if len(recent_lows_price) < 2:
            return {"bullish_divergence": False, "bearish_divergence": False}
        if recent_lows_price.iloc[-1] < recent_lows_price.iloc[-2] and \
           recent_lows_rsi.iloc[-1] > recent_lows_rsi.iloc[-2]:
            return {"bullish_divergence": True, "bearish_divergence": False}
        return {"bullish_divergence": False, "bearish_divergence": False}
