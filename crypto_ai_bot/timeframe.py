"""
Crypto AI Bot v5.7
Timeframe Manager
"""

# تایم‌فریم‌های مورد استفاده
TIMEFRAMES = [
    "15m",
    "1h",
    "4h"
]

# وزن هر تایم‌فریم
TIMEFRAME_WEIGHT = {
    "15m": 0.20,
    "1h": 0.30,
    "4h": 0.50
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
