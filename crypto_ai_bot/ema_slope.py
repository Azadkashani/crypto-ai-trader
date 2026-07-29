"""
EMA Slope Detection
"""

class EMASlope:
    @staticmethod
    def detect(df):
        last = df.iloc[-1]
        prev = df.iloc[-5]
        slopes = {}
        for period in [20, 50, 200]:
            col = f"EMA{period}"
            if col in df.columns:
                slope = (last[col] - prev[col]) / prev[col] * 100 if prev[col] else 0
                slopes[f"EMA{period}_slope_pct"] = round(slope, 4)
        return slopes
