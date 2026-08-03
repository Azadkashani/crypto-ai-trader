"""
Crypto AI Bot v1.2
News & Sentiment Scoring – Multi-level weighted impact
"""

from config import NEWS_WEIGHT_IN_SCORE, SENTIMENT_WEIGHT_IN_SCORE

class NewsScoring:
    @staticmethod
    def calculate(news_list, global_sentiment, asset_sentiment, target_symbol):
        """
        news_list: لیست اخبار (هر خبر شامل 'assets' از NewsMapping و 'sentiment' و 'impact' از NewsAnalyzer)
        global_sentiment: دیکشنری شاخص‌های کل بازار
        asset_sentiment: دیکشنری شاخص‌های مختص دارایی
        target_symbol: نماد هدف (مثلاً 'BTC')
        """
        news_score = 0.0
        sentiment_score = 0.0
        target_base = target_symbol.split("/")[0] if "/" in target_symbol else target_symbol

        for news in news_list:
            assets = news.get("assets", [])
            sentiment = news.get("sentiment", "neutral")
            impact = news.get("impact", "low")
            confidence = news.get("confidence", 0.5)
            # شدت تأثیر خبر
            impact_weight = {"high": 3, "medium": 2, "low": 1}.get(impact, 1)
            # تعیین وزن برای این نماد
            weight = 0
            for asset in assets:
                sym = asset["symbol"]
                if sym == target_base:
                    weight = max(weight, asset["weight"])
                elif sym == "MARKET":
                    weight = max(weight, asset["weight"])
                # اگر اکوسیستم مرتبط
                elif asset["type"] == "ecosystem":
                    # چک کن که target_base در اکوسیستم آن دارایی اصلی باشد
                    # (می‌توان از ECOSYSTEM_MAP برعکس استفاده کرد)
                    pass  # ساده‌سازی: فقط weight خود asset

            if weight == 0:
                continue

            # محاسبه امتیاز خبر
            if sentiment == "bullish":
                news_score += impact_weight * 5 * weight * confidence
            elif sentiment == "bearish":
                news_score -= impact_weight * 5 * weight * confidence

        # Sentiment Score از asset_sentiment (مختص دارایی)
        if asset_sentiment:
            # Funding interpretation
            funding = asset_sentiment.get("funding_interpretation", "neutral")
            if funding == "bullish":
                sentiment_score += 3
            elif funding == "bearish":
                sentiment_score -= 3
            elif funding == "crowded long":
                sentiment_score -= 2  # احتمال برگشت
            elif funding == "crowded short":
                sentiment_score += 2

            # OI state
            oi_state = asset_sentiment.get("oi_state", "")
            if oi_state == "Long Build Up":
                sentiment_score += 4
            elif oi_state == "Short Build Up":
                sentiment_score -= 4
            elif oi_state == "Short Covering":
                sentiment_score += 2
            elif oi_state == "Long Unwinding":
                sentiment_score -= 2

            # Price change (اختیاری)
            price_change = asset_sentiment.get("price_change_pct", 0)
            if price_change > 5:
                sentiment_score += 2
            elif price_change < -5:
                sentiment_score -= 2

        # Global sentiment (کل بازار) با وزن کمتر
        if global_sentiment:
            fng = global_sentiment.get("fear_greed_index", 50)
            if fng > 70:
                sentiment_score -= 3
            elif fng > 55:
                sentiment_score -= 1
            elif fng < 30:
                sentiment_score += 3
            elif fng < 45:
                sentiment_score += 1

        # ضرب در وزن‌های کانفیگ
        news_score *= NEWS_WEIGHT_IN_SCORE
        sentiment_score *= SENTIMENT_WEIGHT_IN_SCORE

        return {
            "news_score": round(news_score, 2),
            "sentiment_score": round(sentiment_score, 2),
        }
