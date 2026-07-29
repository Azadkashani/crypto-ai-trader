"""
VWAP (Volume Weighted Average Price)
"""

class VWAP:
    @staticmethod
    def detect(df):
        if "volume" not in df.columns or len(df) == 0:
            return {"vwap": None, "position": None, "distance_pct": 0}
        vwap_series = (df["close"] * df["volume"]).cumsum() / df["volume"].cumsum()
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
