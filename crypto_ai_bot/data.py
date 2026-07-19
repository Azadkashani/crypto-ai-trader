"""
Crypto AI Bot v5
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
            self.exchange = ccxt.gate({
                "enableRateLimit": True
            })
        else:
            raise Exception("Exchange Not Supported")

    def get_ohlcv(self, symbol):

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

    def get_usdt_symbols(self):

        markets = self.exchange.load_markets()

        symbols = []

        for symbol, market in markets.items():

            if (
                market.get("active", False)
                and market.get("spot", False)
                and market.get("quote") == "USDT"
            ):
                symbols.append(symbol)

        symbols.sort()

        return symbols
