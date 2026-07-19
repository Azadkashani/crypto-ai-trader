"""
Crypto AI Bot v4
Market Data Engine
"""

import ccxt
import pandas as pd

from config import EXCHANGE_NAME
from config import TIMEFRAME
from config import LIMIT


class MarketData:

    def __init__(self):

        if EXCHANGE_NAME.lower() == "gate":
            self.exchange = ccxt.gate()
        else:
            raise Exception("Exchange Not Supported")

    def get_ohlcv(self, symbol):
        def get_usdt_symbols(self):

    markets = self.exchange.load_markets()

    symbols = []

    for symbol in markets:

        market = markets[symbol]

        if (
            market.get("active", False)
            and market.get("spot", False)
            and symbol.endswith("/USDT")
        ):
            symbols.append(symbol)

    symbols.sort()

    return symbols

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=TIMEFRAME,
            limit=LIMIT
        )

        df = pd.DataFrame(
            candles,
            columns=[
                "time",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        )

        df["time"] = pd.to_datetime(
            df["time"],
            unit="ms"
        )

        return df
