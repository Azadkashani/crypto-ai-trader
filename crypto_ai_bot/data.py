"""
Crypto AI Bot v5.7
Market Data Engine (Futures Ready - Volume Sorting)
"""

import ccxt
import pandas as pd

from config import EXCHANGE_NAME, TIMEFRAME, LIMIT


class MarketData:

    def __init__(self):
        if EXCHANGE_NAME.lower() == "gate":
            self.exchange = ccxt.gate({
                "enableRateLimit": True,
                "options": {
                    "defaultType": "swap",   # Futures perpetual
                }
            })
        else:
            raise Exception("Exchange Not Supported")

    # =====================================
    # Single Timeframe Data
    # =====================================
    def get_ohlcv(self, symbol, timeframe=None):
        if timeframe is None:
            timeframe = TIMEFRAME

        candles = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            limit=LIMIT
        )

        df = pd.DataFrame(
            candles,
            columns=["time", "open", "high", "low", "close", "volume"]
        )

        df["time"] = pd.to_datetime(df["time"], unit="ms")
        return df

    # =====================================
    # Multi Timeframe Data
    # =====================================
    def get_multi_timeframe(self, symbol, timeframes):
        data = {}
        for tf in timeframes:
            try:
                data[tf] = self.get_ohlcv(symbol, tf)
            except Exception as e:
                print(f"{symbol} {tf}: {e}")
        return data

    # =====================================
    # USDT Futures Markets (Sorted by 24h Volume)
    # =====================================
    def get_usdt_symbols(self):
        markets = self.exchange.load_markets()
        usdt_futures = []

        # 1. Filter only active USDT perpetual swap markets
        for symbol, market in markets.items():
            if (
                market.get("active", False) and
                market.get("swap", False) and
                market.get("linear", False) and
                market.get("quote") == "USDT"
            ):
                usdt_futures.append(symbol)

        if not usdt_futures:
            return []

        # 2. Fetch tickers for all filtered symbols at once
        try:
            tickers = self.exchange.fetch_tickers(usdt_futures)
        except Exception as e:
            print(f"Error fetching tickers: {e}")
            return sorted(usdt_futures)   # fallback to alphabetical

        # 3. Attach 24h quote volume (USDT volume)
        symbol_volumes = []
        for sym in usdt_futures:
            ticker = tickers.get(sym, {})
            volume = ticker.get("quoteVolume", 0) or 0
            symbol_volumes.append((sym, volume))

        # 4. Sort descending by volume, ascending by symbol for tie
        symbol_volumes.sort(key=lambda x: (-x[1], x[0]))

        sorted_symbols = [s for s, v in symbol_volumes]
        return sorted_symbols
