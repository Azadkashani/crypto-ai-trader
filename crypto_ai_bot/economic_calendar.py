"""
Crypto AI Bot
Economic Calendar – دریافت رویدادهای مهم اقتصادی (ساده)
"""

import requests
from datetime import datetime, timedelta
from config import ECONOMIC_CALENDAR_API_URL, ECONOMIC_CALENDAR_ENABLED

class EconomicCalendar:
    @staticmethod
    def fetch_events():
        if not ECONOMIC_CALENDAR_ENABLED:
            return []
        try:
            # این یک API نمونه است (مثلاً از forexnewsapi یا مشابه)
            # در اینجا یک لیست ثابت برای نمایش استفاده می‌کنیم
            # در محیط واقعی باید API واقعی جایگزین شود
            now = datetime.utcnow()
            return [
                {
                    "title": "FOMC Minutes",
                    "time": (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
                    "country": "USD",
                    "impact": "high",
                    "actual": None,
                    "forecast": None,
                    "previous": None
                }
            ]
        except:
            return []
