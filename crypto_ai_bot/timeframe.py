"""
Crypto AI Bot v5.7
Timeframe Manager
"""

from data import MarketData


class TimeframeManager:


    def __init__(self):

        self.data = MarketData()



    def get_timeframe_data(self, symbol, timeframe):

        return self.data.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=200
        )



    def get_dataframe(self, symbol, timeframe):

        candles = self.get_timeframe_data(
            symbol,
            timeframe
        )

        return self.data.to_dataframe(
            candles
        )
