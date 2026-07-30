"""
Crypto AI Bot v5.7
Timeframe Manager (Intraday)
"""

# تایم‌فریم‌های مورد استفاده (5m, 15m, 1h)
TIMEFRAMES = [
    "5m",
    "15m",
    "1h"
]

# وزن هر تایم‌فریم (تایم‌فریم بالاتر وزن بیشتری دارد)
TIMEFRAME_WEIGHT = {
    "5m": 0.20,
    "15m": 0.30,
    "1h": 0.50
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
