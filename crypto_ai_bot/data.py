"""
Crypto AI Bot v5.7
Market Data Engine
"""

import ccxt
import pandas as pd

from config import (
    EXCHANGE,
    TIMEFRAME,
    LIMIT
)


class MarketData:


    def __init__(self):

        exchange_class = getattr(
            ccxt,
            EXCHANGE
        )

        self.exchange = exchange_class(
            {
                "enableRateLimit": True
            }
        )



    def get_ohlcv(
        self,
        symbol,
        timeframe=TIMEFRAME
    ):

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=LIMIT
        )

        return self.to_dataframe(
            candles
        )



    def get_usdt_symbols(self):

        markets = self.exchange.load_markets()

        symbols = []

        for symbol in markets:

            if (
                symbol.endswith("/USDT")
                and markets[symbol].get("active", False)
            ):

                symbols.append(symbol)


        return symbols



    def to_dataframe(self, candles):

        df = pd.DataFrame(
            candles,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        )


        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            unit="ms"
        )


        return df
