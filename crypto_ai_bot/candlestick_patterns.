"""
Candlestick Pattern Detection
"""

import ta

class CandlestickPatterns:
    @staticmethod
    def detect(df):
        patterns = {}
        patterns["engulfing_bullish"] = bool(ta.candlestick.bullish_engulfing(df["open"], df["high"], df["low"], df["close"]).iloc[-1])
        patterns["engulfing_bearish"] = bool(ta.candlestick.bearish_engulfing(df["open"], df["high"], df["low"], df["close"]).iloc[-1])
        patterns["hammer"] = bool(ta.candlestick.hammer(df["open"], df["high"], df["low"], df["close"]).iloc[-1])
        patterns["shooting_star"] = bool(ta.candlestick.shooting_star(df["open"], df["high"], df["low"], df["close"]).iloc[-1])
        patterns["morning_star"] = bool(ta.candlestick.morning_star(df["open"], df["high"], df["low"], df["close"]).iloc[-1])
        patterns["evening_star"] = bool(ta.candlestick.evening_star(df["open"], df["high"], df["low"], df["close"]).iloc[-1])
        patterns["pinbar"] = patterns["hammer"] or patterns["shooting_star"]
        return patterns
