"""
Crypto AI Bot v5.8
Timeframe Manager (Higher-Timeframe Confirmation)
"""

# تایم‌فریم‌های تأییدکننده MTF — باید بالاتر از تایم‌فریم اصلی معاملاتی (1h) باشند
# طبق اصول تحلیل مولتی‌تایم‌فریم، روند باید توسط تایم‌فریم‌های بزرگ‌تر تأیید شود.
# این لیست عیناً در backtester.py هم استفاده می‌شود تا رفتار لایو و بک‌تست یکسان باشد.
TIMEFRAMES = [
    "4h",
    "1d"
]

# وزن هر تایم‌فریم (تایم‌فریم بالاتر وزن بیشتری دارد)
TIMEFRAME_WEIGHT = {
    "4h": 0.40,
    "1d": 0.60
}


class TimeframeManager:

    @staticmethod
    def get_timeframes():
        return TIMEFRAMES

    @staticmethod
    def get_weights():
        return TIMEFRAME_WEIGHT

    @staticmethod
    def main_timeframe():
        return "1h"
