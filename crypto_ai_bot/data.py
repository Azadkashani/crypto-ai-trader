"""
Crypto AI Bot v1.1
Market Data Engine (Gate.io Futures – Strict Perpetual Filter)
"""

import ccxt
import pandas as pd
from config import EXCHANGE_NAME, TIMEFRAME, LIMIT, MIN_24H_VOLUME


class MarketData:

    def __init__(self):
        if EXCHANGE_NAME.lower() == "gate":
            self.exchange = ccxt.gate({
                "enableRateLimit": True,
                "options": {"defaultType": "swap"}   # Perpetual Futures
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
        """
        دریافت نمادهای فیوچرز دائمی USDT از Gate.io با فیلترهای سخت‌گیرانه:
        - فقط قراردادهای فعال و قابل معامله
        - حذف ربات‌ها، شاخص‌ها، سهام توکنیزه‌شده و ...
        - حداقل حجم معاملات ۲۴ ساعته
        - انتخاب ۵۰ نماد برتر بر اساس حجم
        """
        print("Loading futures markets...")
        markets = self.exchange.load_markets()
        usdt_futures = []

        EXCLUDE_PATTERNS = [
            "BOT", "GRID", "STRATEGY", "SYNTH", "INDEX", "TEST",
            "DEMO", "INTERNAL", "SETTLEMENT", "INACTIVE", "DELISTED",
            "BEAR", "BULL", "UP", "DOWN", "ETF", "TOKENIZED", "STOCK",
            "EQUITY", "SHARE", "MU", "SOXL", "TSLA", "AAPL", "GOOGL"
        ]

        for symbol, market in markets.items():
            # فقط فیوچرز دائمی خطی با پایه USDT
            if not (market.get("active", False) and
                    market.get("swap", False) and
                    market.get("linear", False) and
                    market.get("quote") == "USDT"):
                continue

            info = market.get("info", {})
            if info:
                # بررسی وضعیت معاملاتی
                if info.get("trade_status", "").lower() not in ("tradable", ""):
                    continue
                # حذف نمادهای غیرمجاز
                name_upper = symbol.upper()
                if any(pattern in name_upper for pattern in EXCLUDE_PATTERNS):
                    continue

            usdt_futures.append(symbol)

        if not usdt_futures:
            print("No valid futures contracts found.")
            return []

        print(f"Total Futures Contracts: {len(usdt_futures)}")

        # دریافت حجم ۲۴ ساعته
        try:
            tickers = self.exchange.fetch_tickers(usdt_futures)
        except Exception as e:
            print(f"Error fetching tickers: {e}")
            return sorted(usdt_futures)[:50]

        symbol_volumes = []
        for sym in usdt_futures:
            ticker = tickers.get(sym, {})
            volume = ticker.get("quoteVolume", 0) or 0
            if volume >= MIN_24H_VOLUME:
                symbol_volumes.append((sym, volume))

        symbol_volumes.sort(key=lambda x: (-x[1], x[0]))
        print(f"After Volume Filter (≥{MIN_24H_VOLUME} USDT): {len(symbol_volumes)} contracts")
        print("Top 50 Selected\n")

        return [s for s, v in symbol_volumes[:50]]
