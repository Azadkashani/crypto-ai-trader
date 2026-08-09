"""
Crypto AI Bot v1.2
Market Data Engine (Gate.io Futures – Testnet support)
"""

import ccxt
import pandas as pd
from config import EXCHANGE_NAME, TIMEFRAME, LIMIT, TESTNET


class MarketData:

    def __init__(self):
        if EXCHANGE_NAME.lower() == "gate":
            self.exchange = ccxt.gate({
                "enableRateLimit": True,
                "options": {"defaultType": "swap"}   # Perpetual Futures
            })
            if TESTNET:
                self.exchange.set_sandbox_mode(True)
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
        """
        دریافت فقط قراردادهای فیوچرز دائمی (بدون بارگذاری اسپات).
        """
        # دریافت بازارها با پارامتر swap (فقط فیوچرز)
        markets = self.exchange.fetch_markets(params={"type": "swap"})
        symbols = []
        for market in markets:
            if (
                market.get("active", False) and
                market.get("swap", False) and
                market.get("linear", False) and
                market.get("quote") == "USDT"
            ):
                symbols.append(market["symbol"])
        symbols.sort()
        return symbols
