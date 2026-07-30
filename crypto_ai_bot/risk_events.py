"""
Crypto AI Bot
Risk Event Detection – فیلتر اخبار پرریسک
"""

from datetime import datetime, timedelta
from config import HIGH_IMPACT_WINDOW_MINUTES

class RiskEvents:
    @staticmethod
    def is_high_impact_near(news_list, calendar_events):
        """
        بررسی وجود خبر با اهمیت بالا در بازه زمانی مشخص.
        """
        now = datetime.utcnow()
        window = timedelta(minutes=HIGH_IMPACT_WINDOW_MINUTES)

        # اخبار با impact خیلی بالا
        for news in news_list:
            if news.get("impact") == "very_high":
                try:
                    news_time = datetime.strptime(news["timestamp"], "%a, %d %b %Y %H:%M:%S %z")
                    # اگر خبر تازه‌تر از ۳۰ دقیقه قبل است
                    if now - news_time.replace(tzinfo=None) < window:
                        return True
                except:
                    pass

        # رویدادهای تقویم اقتصادی با impact بالا
        for event in calendar_events:
            if event.get("impact") == "high":
                event_time = datetime.strptime(event["time"], "%Y-%m-%d %H:%M")
                if abs(now - event_time) < window:
                    return True

        return False
