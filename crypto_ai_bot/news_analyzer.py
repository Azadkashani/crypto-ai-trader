"""
Crypto AI Bot v1.1
News Analyzer – manual sentiment & impact
"""

import re

class NewsAnalyzer:
    BULLISH_WORDS = ["bullish", "surge", "rally", "breakout", "upgrade", "buy", "long", "etf", "partnership", "adoption"]
    BEARISH_WORDS = ["bearish", "crash", "plunge", "downgrade", "sell", "short", "hack", "ban", "lawsuit", "delay"]

    @staticmethod
    def analyze(news_item):
        title = news_item.get("title", "").lower()
        bull_score = sum(1 for w in NewsAnalyzer.BULLISH_WORDS if w in title)
        bear_score = sum(1 for w in NewsAnalyzer.BEARISH_WORDS if w in title)
        if bull_score > bear_score:
            sentiment = "bullish"
        elif bear_score > bull_score:
            sentiment = "bearish"
        else:
            sentiment = "neutral"
        impact = "medium" if max(bull_score, bear_score) >= 2 else "low"
        return {**news_item, "sentiment": sentiment, "impact": impact}
