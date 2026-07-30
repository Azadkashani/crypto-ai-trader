"""
Crypto AI Bot
News Analyzer – تحلیل اخبار با قوانین ساده
(بعداً می‌توان با API هوش مصنوعی جایگزین کرد)
"""

import re

class NewsAnalyzer:
    BULLISH_WORDS = ["bullish", "surge", "rally", "breakout", "upgrade", "buy", "long",
                     "etf approved", "partnership", "adoption", "launch", "mainnet"]
    BEARISH_WORDS = ["bearish", "crash", "plunge", "downgrade", "sell", "short",
                     "hack", "exploit", "ban", "regulation crackdown", "lawsuit", "delay"]

    IMPACT_WORDS = {
        "very_high": ["breaking", "urgent", "live", "alert", "confirmed"],
        "high": ["announce", "release", "launch", "ban", "hack", "major"],
        "medium": ["update", "report", "predict", "analyse"],
        "low": ["opinion", "review", "guide"]
    }

    @staticmethod
    def analyze(news_item):
        title = news_item.get("title", "").lower()
        # sentiment
        bull_score = sum(1 for w in NewsAnalyzer.BULLISH_WORDS if w in title)
        bear_score = sum(1 for w in NewsAnalyzer.BEARISH_WORDS if w in title)
        if bull_score > bear_score:
            sentiment = "bullish"
        elif bear_score > bull_score:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        # impact
        impact = "low"
        for level, words in NewsAnalyzer.IMPACT_WORDS.items():
            if any(w in title for w in words):
                impact = level
                break

        return {
            **news_item,
            "sentiment": sentiment,
            "impact": impact
        }
