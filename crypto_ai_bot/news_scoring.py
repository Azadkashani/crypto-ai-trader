"""
Crypto AI Bot
News & Sentiment Scoring
"""
from config import (
    NEWS_WEIGHT_IN_SCORE,
    SENTIMENT_WEIGHT_IN_SCORE,
    NEWS_WEIGHT_IN_CONFIDENCE,
    SENTIMENT_WEIGHT_IN_CONFIDENCE,
)

class NewsScoring:
    @staticmethod
    def calculate(news_list, sentiment_data):
        news_score = 0
        sentiment_score = 0

        # امتیاز اخبار
        for news in news_list:
            impact = news.get("impact", "low")
            sentiment = news.get("sentiment", "neutral")
            weight = {"very_high": 4, "high": 3, "medium": 2, "low": 1}.get(impact, 1)
            if sentiment == "bullish":
                news_score += weight * 5
            elif sentiment == "bearish":
                news_score -= weight * 5

        # امتیاز احساسات
        if sentiment_data:
            fng = sentiment_data.get("fear_greed_index", 50)
            if fng > 70:  # Extreme Greed
                sentiment_score -= 8
            elif fng > 55:  # Greed
                sentiment_score -= 3
            elif fng < 30:  # Fear
                sentiment_score += 8
            elif fng < 45:  # Fear
                sentiment_score += 3

            funding = sentiment_data.get("funding_rate", 0)
            if funding > 0.1:
                sentiment_score += 2  # bullish bias
            elif funding < -0.05:
                sentiment_score -= 2

            oi = sentiment_data.get("oi_delta_pct", 0)
            if oi > 5:
                sentiment_score += 3
            elif oi < -5:
                sentiment_score -= 3

        total_news = news_score * NEWS_WEIGHT_IN_SCORE
        total_sentiment = sentiment_score * SENTIMENT_WEIGHT_IN_SCORE
        conf_news = news_score * NEWS_WEIGHT_IN_CONFIDENCE
        conf_sentiment = sentiment_score * SENTIMENT_WEIGHT_IN_CONFIDENCE

        return {
            "news_score": total_news,
            "sentiment_score": total_sentiment,
            "confidence_news": conf_news,
            "confidence_sentiment": conf_sentiment,
        }
