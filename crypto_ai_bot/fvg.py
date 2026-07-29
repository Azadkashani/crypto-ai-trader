"""
Fair Value Gap (FVG) Detection
"""

class FVG:
    @staticmethod
    def detect(df):
        if len(df) < 3:
            return {"bullish_fvg": False, "bearish_fvg": False, "gap_size": 0, "filled": None}
        last3 = df.iloc[-3:]
        c1 = last3.iloc[0]
        c3 = last3.iloc[2]
        if c3["low"] > c1["high"]:
            gap_size = c3["low"] - c1["high"]
            filled = df["low"].iloc[-1] <= c1["high"]
            return {"bullish_fvg": True, "bearish_fvg": False, "gap_size": gap_size, "filled": filled}
        elif c3["high"] < c1["low"]:
            gap_size = c1["low"] - c3["high"]
            filled = df["high"].iloc[-1] >= c1["low"]
            return {"bullish_fvg": False, "bearish_fvg": True, "gap_size": gap_size, "filled": filled}
        else:
            return {"bullish_fvg": False, "bearish_fvg": False, "gap_size": 0, "filled": None}
