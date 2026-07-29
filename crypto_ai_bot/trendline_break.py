"""
Trendline Break (ساده: شکست خط روند صعودی/نزولی)
"""

class TrendlineBreak:
    @staticmethod
    def detect(df):
        lows = df["low"].tail(20)
        highs = df["high"].tail(20)
        if len(lows) >= 3:
            l1, l2, l3 = lows.iloc[-3], lows.iloc[-2], lows.iloc[-1]
            if l1 < l2 < l3:
                if df["close"].iloc[-1] < l2:
                    return {"trendline_break": "bearish"}
        if len(highs) >= 3:
            h1, h2, h3 = highs.iloc[-3], highs.iloc[-2], highs.iloc[-1]
            if h1 > h2 > h3:
                if df["close"].iloc[-1] > h2:
                    return {"trendline_break": "bullish"}
        return {"trendline_break": None}
