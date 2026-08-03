"""
MACD Divergence
"""

class MACDDivergence:
    @staticmethod
    def detect(df):
        if len(df) < 20:
            return {"bullish_div": False, "bearish_div": False}
        df = df.copy()

        # --- Bearish Divergence: قله بالاتر قیمت + قله پایین‌تر MACD ---
        df["price_peak"] = df["high"].rolling(5, center=True).max()
        df["macd_peak"] = df["MACD_HIST"].rolling(5, center=True).max()
        last_two_price = df["price_peak"].dropna().iloc[-2:]
        last_two_macd = df["macd_peak"].dropna().iloc[-2:]
        bearish_div = False
        if len(last_two_price) >= 2:
            if last_two_price.iloc[-1] > last_two_price.iloc[-2] and last_two_macd.iloc[-1] < last_two_macd.iloc[-2]:
                bearish_div = True

        # --- Bullish Divergence: دره پایین‌تر قیمت + دره بالاتر MACD (قبلاً اصلاً چک نمی‌شد) ---
        df["price_trough"] = df["low"].rolling(5, center=True).min()
        df["macd_trough"] = df["MACD_HIST"].rolling(5, center=True).min()
        last_two_price_low = df["price_trough"].dropna().iloc[-2:]
        last_two_macd_low = df["macd_trough"].dropna().iloc[-2:]
        bullish_div = False
        if len(last_two_price_low) >= 2:
            if last_two_price_low.iloc[-1] < last_two_price_low.iloc[-2] and last_two_macd_low.iloc[-1] > last_two_macd_low.iloc[-2]:
                bullish_div = True

        return {"bullish_div": bullish_div, "bearish_div": bearish_div}
