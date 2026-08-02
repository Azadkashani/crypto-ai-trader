"""
Crypto AI Bot v1.1
Timeframe Manager (Higher TFs for MTF confirmation)
"""

# تایم‌فریم‌های بالاتر از تایم‌فریم اصلی (1h)
TIMEFRAMES = [
    "4h",
    "1d"
]

# وزن هر تایم‌فریم (تایم‌فریم بالاتر وزن بیشتری دارد)
TIMEFRAME_WEIGHT = {
    "4h": 0.30,
    "1d": 0.70
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
