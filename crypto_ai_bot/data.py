"""
Crypto AI Bot v1.1
Market Data Engine (Gate.io Futures – Ultra-Strict Perpetual Swap Filter + No Stock Tokens)
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
        دریافت فقط قراردادهای واقعی فیوچرز دائمی (Perpetual Swap) USDT از Gate.io.
        تمام توکن‌های سهام (AAPLX, MRVL, SOXS, TSLAX, ...) و نمادهای غیرفیوچرزی حذف می‌شوند.
        """
        print("Loading futures markets...")
        markets = self.exchange.load_markets()
        usdt_futures = []

        # الگوهای ممنوعه (حذف تمام نمادهای سهام، ربات‌ها و ...)
        EXCLUDE_PATTERNS = [
            # ربات‌ها، استراتژی‌ها، شاخص‌ها
            "BOT", "GRID", "STRATEGY", "API", "SYNTH", "INDEX",
            "DEX", "ALPHA", "QUAN",
            # تست و دمو
            "TEST", "DEMO", "INTERNAL",
            # وضعیت غیرفعال
            "INACTIVE", "DELISTED", "SETTLEMENT",
            # توکن‌های اهرم‌دار و ETF
            "BEAR", "BULL", "UP", "DOWN", "ETF",
            # سهام توکنیزه‌شده (لیست کامل)
            "TOKENIZED", "STOCK", "EQUITY", "SHARE",
            # پسوندهای معروف توکن‌های سهام
            "X/USDT",     # هر نمادی که به X/USDT ختم شود (مثل AAPLX, TSLAX, ...)
            # لیست صریح سهام معروف (در صورت عدم پوشش با پسوند X)
            "MU/USDT", "SOXL/USDT", "SOXS/USDT", "TSLA/USDT", "AAPL/USDT",
            "GOOGL/USDT", "AMZN/USDT", "MSFT/USDT", "NFLX/USDT",
            "NVDA/USDT", "META/USDT", "BABA/USDT", "SPY/USDT",
            "QQQ/USDT", "AMD/USDT", "INTC/USDT", "PYPL/USDT",
            "DIS/USDT", "V/USDT", "MA/USDT", "JPM/USDT",
            "GME/USDT", "AMC/USDT", "COIN/USDT", "SNAP/USDT",
            "TWTR/USDT", "UBER/USDT", "LYFT/USDT", "ZM/USDT",
            "CXMT/USDT", "SKHYNIX/USDT", "SNDK/USDT",
            "QQQX/USDT", "DRAM/USDT", "MRVL/USDT", "SAMSUNG/USDT",
            "BANK/USDT", "CAP/USDT", "US/USDT",
        ]

        for symbol, market in markets.items():
            # فقط Perpetual Swap (دائمی)
            if market.get("type") != "swap":
                continue

            # فقط Linear USDT
            if not (market.get("linear", False) and market.get("quote") == "USDT"):
                continue

            # فقط فعال
            if not market.get("active", False):
                continue

            # بررسی وضعیت معاملاتی
            info = market.get("info", {})
            if info:
                trade_status = info.get("trade_status", "").lower()
                if trade_status not in ("tradable", ""):
                    continue

            # حذف بر اساس الگوهای ممنوعه
            name_upper = symbol.upper()
            # بررسی ویژه برای پسوند X (سهام)
            if name_upper.endswith("X/USDT") or name_upper.endswith("X:USDT"):
                continue

            if any(pattern.upper() in name_upper for pattern in EXCLUDE_PATTERNS):
                continue

            usdt_futures.append(symbol)

        if not usdt_futures:
            print("No valid futures contracts found.")
            return []

        print(f"Total Valid Perpetual Swaps: {len(usdt_futures)}")

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

        top_symbols = [s for s, v in symbol_volumes[:50]]
        print("Top 50 Selected:")
        for i, sym in enumerate(top_symbols, 1):
            print(f"  {i}. {sym}")

        return top_symbols
