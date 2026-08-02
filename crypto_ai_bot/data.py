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

        # الگوهای ممنوعه (هر نمادی که شامل این کلمات باشد حذف می‌شود)
        EXCLUDE_PATTERNS = [
            # ربات‌ها و استراتژی‌ها
            "BOT", "GRID", "STRATEGY", "API", "SYNTH", "INDEX",
            # تست و دمو
            "TEST", "DEMO", "INTERNAL",
            # وضعیت غیرفعال
            "INACTIVE", "DELISTED", "SETTLEMENT",
            # توکن‌های اهرم‌دار و ETF
            "BEAR", "BULL", "UP", "DOWN", "ETF",
            # سهام توکنیزه‌شده (کاملاً حذف شوند)
            "TOKENIZED", "STOCK", "EQUITY", "SHARE",
            # لیست صریح سهام معروف در Gate.io
            "MU/USDT", "SOXL/USDT", "TSLA/USDT", "AAPL/USDT",
            "GOOGL/USDT", "AMZN/USDT", "MSFT/USDT", "NFLX/USDT",
            "NVDA/USDT", "META/USDT", "BABA/USDT", "SPY/USDT",
            "QQQ/USDT", "AMD/USDT", "INTC/USDT", "PYPL/USDT",
            "DIS/USDT", "V/USDT", "MA/USDT", "JPM/USDT",
            "GME/USDT", "AMC/USDT", "COIN/USDT", "SNAP/USDT",
            "TWTR/USDT", "UBER/USDT", "LYFT/USDT", "ZM/USDT",
            # سایر نمادهای غیرفیوچرز
            "CXMT/USDT", "SKHYNIX/USDT", "SNDK/USDT",
        ]

        for symbol, market in markets.items():
            # فقط فیوچرز دائمی خطی با پایه USDT
            if not (market.get("active", False) and
                    market.get("swap", False) and
                    market.get("linear", False) and
                    market.get("quote") == "USDT"):
                continue

            # بررسی وضعیت معاملاتی از info
            info = market.get("info", {})
            if info:
                trade_status = info.get("trade_status", "").lower()
                if trade_status not in ("tradable", ""):
                    continue

            # بررسی الگوهای ممنوعه
            name_upper = symbol.upper()
            excluded = False
            for pattern in EXCLUDE_PATTERNS:
                if pattern.upper() in name_upper:
                    excluded = True
                    break
            if excluded:
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
            # در صورت خطا، همان لیست فیلترشده (حداکثر ۵۰ تای اول الفبایی) را برگردان
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
