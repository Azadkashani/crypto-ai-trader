"""
Crypto AI Bot v4
Scoring Engine
"""

from config import BUY_SCORE
from config import WATCH_SCORE


class ScoringEngine:

    @staticmethod
    def calculate(df):

        last = df.iloc[-1]

        score = 0
        reasons = []

        # ==========================
        # EMA Alignment
        # ==========================

        if last["EMA20"] > last["EMA50"]:
            score += 25
            reasons.append("EMA20 > EMA50")

        if last["EMA50"] > last["EMA200"]:
            score += 25
            reasons.append("EMA50 > EMA200")

        # ==========================
        # RSI
        # ==========================

        if 45 <= last["RSI"] <= 70:
            score += 20
            reasons.append("Healthy RSI")

        elif last["RSI"] < 30:
            score += 10
            reasons.append("Oversold RSI")

        # ==========================
        # MACD
        # ==========================

        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 20
            reasons.append("Bullish MACD")

        # ==========================
        # Volume
        # ==========================

        avg_volume = df["volume"].tail(20).mean()

        if last["volume"] > avg_volume:
            score += 10
            reasons.append("High Volume")

        return score, reasons

    @staticmethod
    def action(score):

        if score >= BUY_SCORE:
            return "BUY"

        if score >= WATCH_SCORE:
            return "WATCH"

        return "NO TRADE"
