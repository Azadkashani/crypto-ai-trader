"""
Crypto AI Bot v1.1
VWAP – session-based (last 24 hours), not cumulative
"""

import pandas as pd

class VWAP:
    @staticmethod
    def detect(df):
        if "volume" not in df.columns or len(df) == 0:
            return {"vwap": None, "position": None, "distance_pct": 0}

        # استفاده از ۲۴ کندل آخر (معادل یک روز برای تایم‌فریم ۱ ساعته)
        window = 24
        recent = df.tail(window) if len(df) >= window else df
        if recent.empty:
            return {"vwap": None, "position": None, "distance_pct": 0}

        # VWAP استاندارد بر اساس همین پنجره
        typical_price = (recent["high"] + recent["low"] + recent["close"]) / 3
        vwap_series = (typical_price * recent["volume"]).cumsum() / recent["volume"].cumsum()
        vwap_value = vwap_series.iloc[-1]

        current_price = df["close"].iloc[-1]

        if current_price > vwap_value:
            position = "above"
        elif current_price < vwap_value:
            position = "below"
        else:
            position = "at"

        distance_pct = ((current_price - vwap_value) / vwap_value) * 100 if vwap_value else 0

        return {
            "vwap": round(vwap_value, 4),
            "position": position,
            "distance_pct": round(distance_pct, 2)
        }
