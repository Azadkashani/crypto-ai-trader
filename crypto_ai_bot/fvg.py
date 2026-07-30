"""
Fair Value Gap (FVG) Detection (Advanced)
"""

import numpy as np

class FVG:
    @staticmethod
    def detect(df):
        if len(df) < 3:
            return {"bullish_fvg": [], "bearish_fvg": [], "active_fvg": None}
        # کندل‌ها را بررسی می‌کنیم: هرگاه Low کندل سوم > High کندل اول (bullish FVG)
        # یا High کندل سوم < Low کندل اول (bearish FVG)
        gaps = []
        for i in range(2, len(df)):
            c1 = df.iloc[i-2]
            c3 = df.iloc[i]
            if c3["low"] > c1["high"]:
                gaps.append({"type": "bullish", "index": i, "gap_high": c3["low"], "gap_low": c1["high"], "filled": False})
            elif c3["high"] < c1["low"]:
                gaps.append({"type": "bearish", "index": i, "gap_high": c1["low"], "gap_low": c3["high"], "filled": False})
        # بررسی پر شدن
        current_price = df["close"].iloc[-1]
        for g in gaps:
            if g["type"] == "bullish" and df["low"].iloc[-1] <= g["gap_high"]:
                g["filled"] = True
            elif g["type"] == "bearish" and df["high"].iloc[-1] >= g["gap_low"]:
                g["filled"] = True
        # آخرین FVG فعال
        active = None
        for g in reversed(gaps):
            if not g["filled"]:
                active = g
                break
        # جداسازی صعودی/نزولی
        bullish_fvg = [g for g in gaps if g["type"] == "bullish" and not g["filled"]]
        bearish_fvg = [g for g in gaps if g["type"] == "bearish" and not g["filled"]]
        return {
            "bullish_fvg": len(bullish_fvg) > 0,
            "bearish_fvg": len(bearish_fvg) > 0,
            "active_fvg": active,
            "bullish_count": len(bullish_fvg),
            "bearish_count": len(bearish_fvg)
        }
