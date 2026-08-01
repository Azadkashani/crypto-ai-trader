"""
Crypto AI Bot v5.7
Market Data Engine (Binance Futures Demo – Standard CCXT Sandbox)
"""

import ccxt
import pandas as pd
from config import EXCHANGE_NAME, TIMEFRAME, LIMIT, TESTNET, API_KEY, API_SECRET, API_BASE_URL


class MarketData:

    def __init__(self):
        if EXCHANGE_NAME.lower() == "binance":
            # ایجاد نمونهٔ ccxt با کلیدهای API
            self.exchange = ccxt.binance({
                "apiKey": API_KEY,
                "secret": API_SECRET,
                "enableRateLimit": True,
                "options": {"defaultType": "future"}
            })
            if TESTNET:
                # فعال‌سازی sandbox به روش استاندارد CCXT
                self.exchange.set_sandbox_mode(True)
                # تغییر URLها به آدرس دموی فیوچرز
                self.exchange.urls['api'] = {
                    'public': API_BASE_URL,
                    'private': API_BASE_URL,
                    'fapiPublic': API_BASE_URL,
                    'fapiPrivate': API_BASE_URL,
                }
            else:
                # در حالت واقعی هیچ تغییری نده
                pass
        elif EXCHANGE_NAME.lower() == "gate":
            self.exchange = ccxt.gate({
                "apiKey": API_KEY,
                "secret": API_SECRET,
                "enableRateLimit": True,
                "options": {"defaultType": "swap"}
            })
        else:
            raise Exception("Exchange Not Supported")

        # چاپ آدرس نهایی برای تأیید
        if TESTNET:
            print(f"🌐 Binance Demo API Base URL: {self.exchange.urls['api']['fapiPublic']}")
        else:
            print(f"🌐 Binance Live API Base URL: {self.exchange.urls['api']['fapiPublic']}")

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
                market.get("swap", False) and
                market.get("linear", False) and
                market.get("quote") == "USDT"
            ):
                symbols.append(symbol)
        symbols.sort()
        return symbols
