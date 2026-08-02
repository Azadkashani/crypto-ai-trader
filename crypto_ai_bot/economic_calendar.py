"""
Crypto AI Bot v1.1
Economic Calendar – safe mock (events are in the past, will not block trades)
"""

from config import ENABLE_ECONOMIC_CALENDAR

class EconomicCalendar:
    @staticmethod
    def fetch_events():
        """
        اگر ENABLE_ECONOMIC_CALENDAR = True باشد، رویدادهای mock بازگردانده می‌شوند.
        این رویدادها در گذشته قرار دارند و هرگز به‌عنوان «نزدیک» شناسایی نمی‌شوند.
        برای استفادهٔ واقعی باید یک API تقویم اقتصادی متصل شود.
        """
        if not ENABLE_ECONOMIC_CALENDAR:
            return []

        # این تاریخ‌ها ثابت و متعلق به گذشته هستند.
        return [
            {
                "title": "FOMC Minutes (mock)",
                "time": "2020-01-01 12:00",
                "country": "USD",
                "impact": "high",
                "actual": None,
                "forecast": None,
                "previous": None
            },
            {
                "title": "CPI Data (mock)",
                "time": "2020-01-01 12:00",
                "country": "USD",
                "impact": "high",
                "actual": None,
                "forecast": None,
                "previous": None
            },
        ]
