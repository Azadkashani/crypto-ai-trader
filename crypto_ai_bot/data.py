"""
Crypto AI Bot v1.1
Market Data Engine (Gate.io Futures – Strict Perpetual Filter + Extra Clean)
"""

import ccxt
import pandas as pd
from config import EXCHANGE_NAME, TIMEFRAME, LIMIT, MIN_24H_VOLUME


class MarketData:

    def __init__(self):
        if EXCHANGE_NAME.lower() == "gate":
            self.exchange = ccxt.gate({
                "enableRateLimit": True,
                "options": {"defaultType": "swap"}
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
        print("Loading futures markets...")
        markets = self.exchange.load_markets()
        usdt_futures = []

        # الگوهای ممنوعهٔ گسترده‌تر
        EXCLUDE_PATTERNS = [
            # ربات‌ها، شاخص‌ها، توکن‌های مصنوعی
            "BOT", "GRID", "STRATEGY", "API", "SYNTH", "INDEX",
            "DEX", "ALPHA",  # ← حذف DEX/BOT/Alpha
            # تست و دمو
            "TEST", "DEMO", "INTERNAL",
            # وضعیت غیرفعال
            "INACTIVE", "DELISTED", "SETTLEMENT",
            # توکن‌های اهرم‌دار و ETF
            "BEAR", "BULL", "UP", "DOWN", "ETF",
            # سهام توکنیزه‌شده
            "TOKENIZED", "STOCK", "EQUITY", "SHARE",
            # لیست صریح سهام و نمادهای غیرفیوچرز
            "MU/USDT", "SOXL/USDT", "TSLA/USDT", "AAPL/USDT",
            "GOOGL/USDT", "AMZN/USDT", "MSFT/USDT", "NFLX/USDT",
            "NVDA/USDT", "META/USDT", "BABA/USDT", "SPY/USDT",
            "QQQ/USDT", "AMD/USDT", "INTC/USDT", "PYPL/USDT",
            "DIS/USDT", "V/USDT", "MA/USDT", "JPM/USDT",
            "GME/USDT", "AMC/USDT", "COIN/USDT", "SNAP/USDT",
            "TWTR/USDT", "UBER/USDT", "LYFT/USDT", "ZM/USDT",
            "CXMT/USDT", "SKHYNIX/USDT", "SNDK/USDT",
            # موارد جدید که گزارش شده‌اند
            "QQQX/USDT",          # ← حذف مستقیم
        ]

        for symbol, market in markets.items():
            # فقط فیوچرز دائمی خطی USDT
            if not (market.get("active", False) and
                    market.get("swap", False) and
                    market.get("linear", False) and
                    market.get("quote") == "USDT"):
                continue

            # بررسی وضعیت معاملاتی
            info = market.get("info", {})
            if info:
                trade_status = info.get("trade_status", "").lower()
                if trade_status not in ("tradable", ""):
                    continue

            # حذف بر اساس الگوها
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
