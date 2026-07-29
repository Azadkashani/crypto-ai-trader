"""
ATR Volatility Filter
"""

import pandas as pd

class ATRVolatility:
    @staticmethod
    def detect(df):
        atr = df["ATR"].iloc[-1]
        avg_atr = df["ATR"].tail(20).mean()
        if pd.isna(avg_atr) or avg_atr == 0:
            return {"volatility": "unknown", "atr_ratio": 0}
        ratio = atr / avg_atr
        if ratio < 0.7:
            vol = "Low Volatility"
        elif ratio > 1.3:
            vol = "High Volatility"
        else:
            vol = "Normal"
        return {"volatility": vol, "atr_ratio": round(ratio, 2)}
