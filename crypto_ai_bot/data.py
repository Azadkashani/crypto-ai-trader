"""
Crypto AI Bot v1.1
Market Data Engine (Gate.io Futures – Ultra-Strict + No Grid Bots)
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
        تمام Grid Bots، توکن‌های سهام، ربات‌ها، ETFها و نمادهای غیرفیوچرزی **کاملاً** حذف می‌شوند.
        اگر تعداد کمتر از ۵۰ باشد، همان تعداد تحلیل می‌شود.
        """
        print("Loading futures markets...")
        markets = self.exchange.load_markets()
        usdt_futures = []

        EXCLUDE_PATTERNS = [
            "BOT", "GRID", "STRATEGY", "API", "SYNTH", "INDEX",
            "DEX", "ALPHA", "QUAN",
            "TEST", "DEMO", "INTERNAL",
            "INACTIVE", "DELISTED", "SETTLEMENT",
            "BEAR", "BULL", "UP", "DOWN", "ETF",
            "TOKENIZED", "STOCK", "EQUITY", "SHARE",
            "X/USDT",   # تمام سهام
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
            "HOME/USDT", "GIGGLE/USDT", "RATS/USDT", "PUMP/USDT",
            "SNOW/USDT", "EWY/USDT", "XIAOMI/USDT", "BE/USDT",
            "ICNT/USDT", "VANRY/USDT", "LITE/USDT", "SKYAI/USDT",
            "ZHIPU/USDT", "NBIS/USDT", "BICO/USDT", "TAO/USDT",
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

            # بررسی کامل info برای فیلتر Grid
            info = market.get("info", {})
            if info:
                trade_status = info.get("trade_status", "").lower()
                if trade_status not in ("tradable", ""):
                    continue

                # فیلتر نهایی: هر فیلدی که "grid" در آن باشد → حذف
                info_str = str(info).lower()
                if "grid" in info_str:
                    continue

            # حذف بر اساس الگوهای ممنوعه
            name_upper = symbol.upper()
            if name_upper.endswith("X/USDT") or name_upper.endswith("X:USDT"):
                continue

            if any(pattern.upper() in name_upper for pattern in EXCLUDE_PATTERNS):
                continue

            usdt_futures.append(symbol)

        if not usdt_futures:
            print("No valid futures contracts found.")
            return []

        print(f"Total Valid Perpetual Swaps (no grid): {len(usdt_futures)}")

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
