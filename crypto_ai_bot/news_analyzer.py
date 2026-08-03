"""
Crypto AI Bot v1.2
News Analyzer – Context-aware sentiment with confidence and impact
"""

import re

class NewsAnalyzer:
    # الگوهای مثبت/منفی با وزن
    PATTERNS = [
        # (regex, sentiment, base_impact, confidence)
        (r'\b(?:surge|rally|soar|jump|spike|bullish|breakout|upgrade|buy|long|etf\s+approv|partnership|adoption|launch|mainnet|upgrade|inflow|accumulation|whale\s+buy)\b', "bullish", "high", 0.9),
        (r'\b(?:crash|plunge|dump|fall|drop|bearish|downgrade|sell|short|hack|exploit|ban|lawsuit|delay|rejection|outflow|distribution|sell\s+pressure|whale\s+sell)\b', "bearish", "high", 0.9),
        (r'\b(?:investigation|regulatory|sec\s+warning|cftc|fine|penalty|restrict)\b', "bearish", "high", 0.85),
        (r'\b(?:approval\s+delay|postpone|suspend|halt|freeze)\b', "bearish", "medium", 0.8),
        (r'\b(?:upgrade|patch|fix|improve|enhance)\b', "bullish", "low", 0.7),
        (r'\b(?:downtime|outage|bug|vulnerability|attack|phish)\b', "bearish", "medium", 0.8),
        (r'\b(?:record\s+high|all-time\s+high|ath)\b', "bullish", "medium", 0.85),
        (r'\b(?:record\s+low|all-time\s+low|atl)\b', "bearish", "medium", 0.85),
    ]

    @staticmethod
    def analyze(news_item):
        title = news_item.get("title", "").lower()
        best_sentiment = "neutral"
        best_impact = "low"
        best_confidence = 0.5
        score = 0

        for pattern, sentiment, impact, conf in NewsAnalyzer.PATTERNS:
            if re.search(pattern, title):
                score += 1 if sentiment == "bullish" else -1
                if conf > best_confidence:
                    best_confidence = conf
                if impact == "high" or (impact == "medium" and best_impact != "high"):
                    best_impact = impact

        if score > 0:
            best_sentiment = "bullish"
        elif score < 0:
            best_sentiment = "bearish"

        return {
            **news_item,
            "sentiment": best_sentiment,
            "confidence": best_confidence,
            "impact": best_impact
        }
