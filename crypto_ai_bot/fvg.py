"""
Fair Value Gap (FVG) Detection
"""

import numpy as np

class FVG:
    @staticmethod
    def detect(df):
        if len(df) < 3:
            return {"bullish_fvg": False, "bearish_fvg": False, "gap_size": 0, "filled": None}
        # سه کندل آخر
        last3 = df.iloc[-3:]
        c1 = last3.iloc[0]  # کندل اول
        c3 = last3.iloc[2]  # کندل سوم
        # Bullish FVG: Low کندل سوم > High کندل اول (شکاف صعودی)
        if c3["low"] > c1["high"]:
            gap_size = c3["low"] - c1["high"]
            filled = False
            # بررسی پر شدن: آیا قیمت به داخل شکاف برگشته؟
            if df["low"].iloc[-1] <= c1["high"]:
                filled = True
            return {"bullish_fvg": True, "bearish_fvg": False, "gap_size": gap_size, "filled": filled}
        # Bearish FVG: High کندل سوم < Low کندل اول
        elif c3["high"] < c1["low"]:
            gap_size = c1["low"] - c3["high"]
            filled = False
            if df["high"].iloc[-1] >= c1["low"]:
                filled = True
            return {"bullish_fvg": False, "bearish_fvg": True, "gap_size": gap_size, "filled": filled}
        else:
            return {"bullish_fvg": False, "bearish_fvg": False, "gap_size": 0, "filled": None}
