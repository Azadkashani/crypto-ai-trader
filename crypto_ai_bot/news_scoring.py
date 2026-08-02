"""
Crypto AI Bot v1.1
News & Sentiment Scoring (per-symbol with BTC multiplier)
"""

from config import NEWS_WEIGHT_IN_SCORE, SENTIMENT_WEIGHT_IN_SCORE

class NewsScoring:
    @staticmethod
    def calculate(news_list, sentiment_data, target_symbol):
        news_score = 0
        sentiment_score = 0
        base_coin = target_symbol.split("/")[0] if "/" in target_symbol else target_symbol

        for news in news_list:
            impact = news.get("impact", "low")
            sentiment = news.get("sentiment", "neutral")
            weight = {"high": 3, "medium": 2, "low": 1}.get(impact, 1)
            multiplier = 1.0
            if base_coin != "BTC" and "BTC" in news.get("currencies", []):
                multiplier = 0.5
            if sentiment == "bullish":
                news_score += weight * 5 * multiplier
            elif sentiment == "bearish":
                news_score -= weight * 5 * multiplier

        # Sentiment مستقل
        if sentiment_data:
            fng = sentiment_data.get("fear_greed_index", 50)
            if fng > 70:
                sentiment_score -= 8
            elif fng > 55:
                sentiment_score -= 3
            elif fng < 30:
                sentiment_score += 8
            elif fng < 45:
                sentiment_score += 3

            funding = sentiment_data.get("funding_rate", 0)
            if funding > 0.1:
                sentiment_score += 2
            elif funding < -0.05:
                sentiment_score -= 2

            oi = sentiment_data.get("oi_delta_pct", 0)
            if oi > 5:
                sentiment_score += 3
            elif oi < -5:
                sentiment_score -= 3

        return {
            "news_score": news_score * NEWS_WEIGHT_IN_SCORE,
            "sentiment_score": sentiment_score * SENTIMENT_WEIGHT_IN_SCORE,
        }
