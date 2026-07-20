%%writefile timeframe.py

"""
Crypto AI Bot v5.7
Timeframe Manager
"""

from config import MTF_TIMEFRAMES


class TimeframeManager:


    @staticmethod
    def get_timeframes():

        return MTF_TIMEFRAMES


    @staticmethod
    def main_timeframe():

        return "1h"
