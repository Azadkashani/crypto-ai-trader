"""
Market Regime Detection
"""

import pandas as pd

class MarketRegime:
    @staticmethod
    def detect(df):
        adx = df["ADX"].iloc[-1]
        atr = df["ATR"].iloc[-1]
        avg_atr = df["ATR"].tail(20).mean()
        if pd.isna(adx) or pd.isna(atr):
            return {"regime": "unknown"}
        if adx > 25:
            if atr > avg_atr * 1.2:
                return {"regime": "Trending - High Volatility"}
            else:
                return {"regime": "Trending"}
        elif adx < 15:
            return {"regime": "Ranging / Choppy"}
        else:
            return {"regime": "Moderate"}
