"""
Crypto AI Bot v1.1
Economic Calendar – simulated high-impact events
"""

from datetime import datetime, timedelta

class EconomicCalendar:
    @staticmethod
    def fetch_events():
        """
        ⚠️ TODO: این تابع باید به یک منبع واقعی اقتصادی (API واقعی economic calendar) وصل شود.

        نسخه‌ی قبلی همیشه دو رویداد ساختگی با آفست ثابت (۴۵ و ۹۰ دقیقه از "الان") برمی‌گرداند.
        چون این آفست‌ها نسبت به لحظه‌ی فراخوانی دوباره تولید می‌شدند، اگر ENABLE_ECONOMIC_CALENDAR
        فعال می‌شد، RiskEvents.is_high_impact_near همیشه یک رویداد "high impact" نزدیک پیدا می‌کرد
        و ربات برای همیشه در حالت WATCH اجباری (Macro Risk Active) گیر می‌کرد.
        تا زمان اتصال به API واقعی، لیست خالی برمی‌گردانیم تا این قفل دائمی رخ ندهد.
        """
        return []
