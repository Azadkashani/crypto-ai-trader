"""
Crypto AI Bot v5.7
Market Data Engine (Gate.io Futures Perpetual)
"""

import ccxt
import pandas as pd
from config import EXCHANGE_NAME, TIMEFRAME, LIMIT


class MarketData:

    def __init__(self):
        if EXCHANGE_NAME.lower() == "gate":
            self.exchange = ccxt.gate({
                "enableRateLimit": True,
                "options": {"defaultType": "swap"}   # فیوچرز دائمی
            })
        else:
            raise Exception("Exchange Not Supported")

    def get_ohlcv(self, symbol, timeframe=None):
        if timeframe is None:
            timeframe = TIMEFRAME
        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=LIMIT
        )
        df = pd.DataFrame(candles, columns=["time", "open", "high", "low", "close", "volume"])
        df["time"] = pd.to_datetime(df["time"], unit="ms")
        return df

    def get_multi_timeframe(self, symbol, timeframes):
        data = {}
        for tf in timeframes:
            try:
                data[tf] = self.get_ohlcv(symbol, tf)
            except Exception as e:
                print(f"{symbol} {tf}: {e}")
        return data

    def get_usdt_symbols(self):
        markets = self.exchange.load_markets()
        symbols = []
        for symbol, market in markets.items():
            if (
                market.get("active", False) and
                market.get("swap", False) and      # فیوچرز دائمی
                market.get("linear", False) and    # linear = USDT margined
                market.get("quote") == "USDT"
            ):
                symbols.append(symbol)
        symbols.sort()
        return symbols
