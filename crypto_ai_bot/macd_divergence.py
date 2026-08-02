"""
Crypto AI Bot v1.1
MACD Divergence – full bullish & bearish detection
"""

import pandas as pd

class MACDDivergence:
    @staticmethod
    def detect(df):
        if len(df) < 20:
            return {"bullish_div": False, "bearish_div": False}

        df = df.copy()
        # پنجره‌ی ۵ برای پیدا کردن قله‌ها/کف‌های محلی
        window = 5

        # ----- واگرایی نزولی (Bearish) -----
        df["price_high"] = df["high"].rolling(window, center=True).max()
        df["macd_high"] = df["MACD_HIST"].rolling(window, center=True).max()

        last_two_price_high = df["price_high"].dropna().iloc[-2:]
        last_two_macd_high = df["macd_high"].dropna().iloc[-2:]

        bearish = False
        if len(last_two_price_high) == 2 and len(last_two_macd_high) == 2:
            if last_two_price_high.iloc[-1] > last_two_price_high.iloc[-2] and \
               last_two_macd_high.iloc[-1] < last_two_macd_high.iloc[-2]:
                bearish = True

        # ----- واگرایی صعودی (Bullish) -----
        df["price_low"] = df["low"].rolling(window, center=True).min()
        df["macd_low"] = df["MACD_HIST"].rolling(window, center=True).min()

        last_two_price_low = df["price_low"].dropna().iloc[-2:]
        last_two_macd_low = df["macd_low"].dropna().iloc[-2:]

        bullish = False
        if len(last_two_price_low) == 2 and len(last_two_macd_low) == 2:
            if last_two_price_low.iloc[-1] < last_two_price_low.iloc[-2] and \
               last_two_macd_low.iloc[-1] > last_two_macd_low.iloc[-2]:
                bullish = True

        return {"bullish_div": bullish, "bearish_div": bearish}
