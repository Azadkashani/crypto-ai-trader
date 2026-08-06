"""
Crypto AI Bot v1.2
Timeframe Manager (5m main, 15m and 1h for MTF)
"""

# تایم‌فریم‌های تأیید (MTF) – بالاتر از تایم‌فریم اصلی 5m
TIMEFRAMES = [
    "15m",
    "1h"
]

# وزن هر تایم‌فریم (تایم‌فریم بالاتر وزن بیشتری دارد)
TIMEFRAME_WEIGHT = {
    "15m": 0.30,
    "1h": 0.70
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
        return "5m"
