"""
VWAP (Volume Weighted Average Price) - Session/Daily Anchored
"""

import pandas as pd


class VWAP:
    @staticmethod
    def detect(df):
        if "volume" not in df.columns or len(df) == 0:
            return {"vwap": None, "position": None, "distance_pct": 0}

        # قبلاً VWAP از ابتدای کل دیتافریم (مثلاً ۲۰۰ کندل عقب) تجمعی محاسبه می‌شد
        # و هیچ‌وقت ریست نمی‌شد که با تعریف استاندارد VWAP (ریست روزانه/سشنی) در تضاد بود.
        # اینجا در صورت وجود ستون time، VWAP هر روز (UTC) از نو شروع می‌شود.
        if "time" in df.columns:
            session_key = pd.to_datetime(df["time"]).dt.date
            pv = df["close"] * df["volume"]
            cum_pv = pv.groupby(session_key).cumsum()
            cum_vol = df["volume"].groupby(session_key).cumsum()
            vwap_series = cum_pv / cum_vol
        else:
            # fallback: پنجره‌ی محدود (۲۴ کندل آخر) به‌جای کل تاریخچه
            window = min(24, len(df))
            recent = df.tail(window)
            vwap_series = (recent["close"] * recent["volume"]).cumsum() / recent["volume"].cumsum()

        vwap_value = vwap_series.iloc[-1]
        current_price = df["close"].iloc[-1]
        if current_price > vwap_value:
            position = "above"
        elif current_price < vwap_value:
            position = "below"
        else:
            position = "at"
        distance = ((current_price - vwap_value) / vwap_value) * 100
        return {
            "vwap": round(vwap_value, 4),
            "position": position,
            "distance_pct": round(distance, 2)
        }
