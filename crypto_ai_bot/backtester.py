"""
Crypto AI Bot
Backtester Engine – Full version with CSV support, Mock, API (MEXC, Bybit, etc.), and internal MTF
"""

import pandas as pd
import numpy as np
import ccxt
import os
from datetime import timedelta
from indicators import IndicatorEngine
from market_structure import MarketStructure
from scoring import ScoringEngine
from decision_engine import DecisionEngine
from trade_engine import TradeEngine
from portfolio import Portfolio
from equity_curve import EquityCurve
from performance import Performance
from backtest_report import BacktestReport
from mtf_engine import MTFEngine
from advanced_analytics import AdvancedAnalytics
from timeframe import TIMEFRAME_WEIGHT


class CausalMarketStructure:
    @staticmethod
    def analyze(df):
        return MarketStructure.analyze(df)


class Backtester:
    def __init__(self, symbols, start_date, end_date, timeframe,
                 initial_capital, risk_per_trade, leverage, max_open_trades,
                 trailing_stop, trailing_activation,
                 fee, slippage, spread, max_hold_bars, output_dir,
                 exchange_name='binance', use_mock=False):
        self.symbols = symbols
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        self.timeframe = timeframe
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.leverage = leverage
        self.max_open_trades = max_open_trades
        self.trailing_stop = trailing_stop
        self.trailing_activation = trailing_activation
        self.fee = fee
        self.slippage = slippage
        self.spread = spread
        self.max_hold_bars = max_hold_bars
        self.output_dir = output_dir
        self.exchange_name = exchange_name
        self.use_mock = use_mock

        self.exchange = None
        if not use_mock and exchange_name in ('binance', 'gate', 'kucoin', 'mexc', 'bybit'):
            if exchange_name == 'mexc':
                self.exchange = ccxt.mexc({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'swap'}
                })
            elif exchange_name == 'bybit':
                self.exchange = ccxt.bybit({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'future'}
                })
            elif exchange_name == 'kucoin':
                self.exchange = ccxt.kucoinfutures({'enableRateLimit': True})
            elif exchange_name == 'gate':
                self.exchange = ccxt.gate({'enableRateLimit': True})
            else:  # binance
                self.exchange = ccxt.binance({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'future'}
                })

        self.portfolio = Portfolio(initial_capital, risk_per_trade, leverage, fee, slippage, spread)
        self.trade_engine = TradeEngine(self.portfolio, trailing_stop, trailing_activation, max_hold_bars)
        self.equity_curve = EquityCurve()
        # data_engine=None در حالت آفلاین/mock: یعنی موارد وابسته به صرافی زنده
        # (Open Interest, Funding Rate, Correlation) به‌صورت امن نادیده گرفته می‌شوند.
        self.advanced_analytics_engine = AdvancedAnalytics(data_engine=self if self.exchange else None)

        self.data = {}
        self.indicators = {}
        self.market_structures = {}
        self.advanced_analytics = {}

    def _generate_mock_data(self, sym):
        np.random.seed(42)
        dates = pd.date_range(self.start_date, self.end_date, freq=self.timeframe)
        n = len(dates)
        prices = [100]
        for _ in range(1, n):
            prices.append(prices[-1] * (1 + np.random.normal(0, 0.02)))
        df = pd.DataFrame({
            'time': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.005))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.005))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(100, 1000, n)
        })
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        return df

    def load_data(self):
        for sym in self.symbols:
            base_name = sym.replace("/", "").replace(":", "")
            csv_filename = f"{base_name}_{self.timeframe}.csv"
            paths_to_try = [
                os.path.join(self.output_dir, csv_filename),
                os.path.join(os.getcwd(), csv_filename),
                csv_filename
            ]
            found = False
            for csv_path in paths_to_try:
                if os.path.exists(csv_path):
                    try:
                        df = pd.read_csv(csv_path)
                        print(f"Loaded CSV: {csv_path}")
                        col_map = {
                            'open_time': 'time',
                            'timestamp': 'time', 'date': 'time', 'datetime': 'time',
                            'open': 'open', 'Open': 'open',
                            'high': 'high', 'High': 'high',
                            'low': 'low', 'Low': 'low',
                            'close': 'close', 'Close': 'close',
                            'volume': 'volume', 'Volume': 'volume', 'vol': 'volume'
                        }
                        df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)
                        if 'time' in df.columns:
                            df['time'] = pd.to_datetime(df['time'])
                        else:
                            print(f"Warning: no time column for {sym}, assuming sequential rows")
                            df['time'] = pd.date_range(start=self.start_date, periods=len(df), freq=self.timeframe)
                        df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
                        df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                        if df.empty:
                            print(f"No data in range for {sym} in CSV")
                            break
                        df = df.reset_index(drop=True)
                        self.data[sym] = df
                        self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                        print(f"Prepared {len(df)} candles for {sym}")
                        found = True
                        break
                    except Exception as e:
                        print(f"Error reading CSV {csv_path}: {e}")
            if found:
                continue

            if self.use_mock:
                df = self._generate_mock_data(sym)
                self.data[sym] = df
                self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                print(f"Generated {len(df)} mock candles for {sym}")
                continue

            if self.exchange is not None:
                try:
                    ohlcv = self.exchange.fetch_ohlcv(
                        sym,
                        timeframe=self.timeframe,
                        since=int(self.start_date.timestamp() * 1000),
                        limit=1000
                    )
                    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                    df['time'] = pd.to_datetime(df['time'], unit='ms')
                    df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                    if not df.empty:
                        df = df.reset_index(drop=True)
                        self.data[sym] = df
                        self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                        print(f"Loaded {len(df)} candles for {sym} from API")
                        continue
                except Exception as e:
                    print(f"API failed for {sym}: {e}")

            try:
                import yfinance as yf
                ticker = sym.replace("/", "-")
                yf_ticker = yf.Ticker(ticker)
                df = yf_ticker.history(
                    start=self.start_date.strftime('%Y-%m-%d'),
                    end=(self.end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    interval=self.timeframe
                )
                if not df.empty:
                    df.reset_index(inplace=True)
                    df.rename(columns={'Date': 'time', 'Datetime': 'time', 'Open': 'open', 'High': 'high',
                                       'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
                    df['time'] = pd.to_datetime(df['time'])
                    df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
                    df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                    if df.empty:
                        continue
                    df = df.reset_index(drop=True)
                    self.data[sym] = df
                    self.indicators[sym] = IndicatorEngine.calculate(df.copy())
                    print(f"Loaded {len(df)} candles for {sym} from yfinance")
            except Exception as e:
                print(f"yfinance failed for {sym}: {e}")

    @staticmethod
    def _pandas_freq(tf):
        """تبدیل رشته تایم‌فریم سبک ccxt (4h, 1d, ...) به فرکانس قابل‌فهم pandas.resample"""
        unit_map = {"m": "min", "h": "h", "d": "D", "w": "W"}
        num = "".join(ch for ch in tf if ch.isdigit()) or "1"
        unit = "".join(ch for ch in tf if ch.isalpha())
        return f"{num}{unit_map.get(unit, 'h')}"

    def _calculate_mtf_signal(self, df):
        """
        محاسبه سیگنال مولتی‌تایم‌فریم دقیقاً هم‌راستا با scanner.py (حالت لایو):
        از همان TIMEFRAME_WEIGHT در timeframe.py استفاده می‌کند (تایم‌فریم‌های بالاتر: 4h, 1d)
        تا رفتار بک‌تست و لایو یکسان باشد.
        """
        from trend import TrendEngine
        bullish = 0.0
        bearish = 0.0
        for tf, weight in TIMEFRAME_WEIGHT.items():
            try:
                freq = self._pandas_freq(tf)
                df_tf = df.resample(freq, on='time').agg({
                    'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
                }).dropna()
                if len(df_tf) < 20:
                    continue
                df_tf_ind = IndicatorEngine.calculate(df_tf.copy())
                trend_tf = TrendEngine.detect(df_tf_ind)
            except Exception:
                continue
            if trend_tf == "Bullish":
                bullish += weight
            elif trend_tf == "Bearish":
                bearish += weight

        if bullish >= 0.7:
            return "Strong Bullish"
        elif bearish >= 0.7:
            return "Strong Bearish"
        elif bullish > bearish:
            return "Bullish"
        elif bearish > bullish:
            return "Bearish"
        return "Neutral"

    def _analyze_at(self, sym, df_slice):
        """
        تحلیل ساختار بازار و آنالیز پیشرفته را فقط روی داده‌ی تا لحظه‌ی جاری (df_slice)
        محاسبه می‌کند.

        ⚠️ نسخه‌ی قبلی (compute_analysis) این تحلیل‌ها را یک‌بار روی کل دیتافریم
        (از ابتدا تا انتهای بازه‌ی بک‌تست) محاسبه می‌کرد و همان نتیجه‌ی ثابت را برای
        تمام کندل‌های شبیه‌سازی دوباره استفاده می‌کرد. این یعنی Look-Ahead Bias شدید:
        تصمیم‌گیری در هر لحظه از بک‌تست، اطلاعات آینده (تا انتهای بازه) را می‌دید.
        این متد آن مشکل را با محاسبه‌ی دوباره‌ی ساختار بازار برای هر لحظه، فقط بر
        اساس داده‌ی موجود تا همان لحظه، برطرف می‌کند.
        """
        ms = CausalMarketStructure.analyze(df_slice)
        try:
            advanced_data = self.advanced_analytics_engine.analyze(
                df_slice, market_structure=ms, symbol=sym
            )
        except Exception:
            advanced_data = None
        return ms, advanced_data

    def run(self):
        print("Loading historical data...")
        self.load_data()

        self.symbols = [s for s in self.symbols if s in self.data]
        if not self.symbols:
            print("No valid symbols for backtest.")
            return

        # حداقل تعداد کندل لازم برای معنادار بودن اندیکاتورها (EMA200 و غیره)
        min_bars_required = 210

        all_times = set()
        for sym in self.data:
            all_times.update(self.data[sym]['time'].tolist())
        all_times = sorted(all_times)
        time_index = pd.DatetimeIndex(all_times)

        print(f"Running backtest from {time_index[0]} to {time_index[-1]}...")
        self.equity_curve.record(time_index[0], self.initial_capital)

        for ts in time_index[1:]:
            self.trade_engine.update(ts, self.data, self.indicators, self.market_structures)

            for sym in self.data:
                df = self.data[sym]
                idx = df[df['time'] == ts].index
                if len(idx) == 0:
                    continue
                idx = idx[0]

                # فقط داده‌ی تا همین لحظه (idx) در اختیار تحلیل قرار می‌گیرد؛
                # هیچ کندل آینده‌ای دیده نمی‌شود (رفع Look-Ahead Bias).
                if idx + 1 < min_bars_required:
                    continue
                df_slice = self.indicators[sym].iloc[:idx + 1]
                row = df_slice.iloc[-1]

                if not self.trade_engine.is_position_open(sym):
                    ms, advanced_data = self._analyze_at(sym, df_slice)
                    from trend import TrendEngine
                    strength = TrendEngine.strength(df_slice)

                    # محاسبه MTF فقط از داده‌ی تا لحظه‌ی جاری
                    mtf_signal = self._calculate_mtf_signal(df_slice)

                    analysis = ScoringEngine.calculate(
                        df_slice,
                        mtf_signal,
                        market_structure=ms,
                        strength=strength,
                        advanced_data=advanced_data,
                    )

                    decision = DecisionEngine.evaluate(
                        df_slice,
                        ms,
                        mtf_signal,
                        strength,
                        advanced_data,
                        analysis["score"],
                        analysis["breakout"],
                        analysis["reasons"],
                        analysis["warnings"],
                        risk_event=False
                    )

                    action = decision["action"]
                    if action in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"):
                        if len(self.trade_engine.open_trades) < self.max_open_trades:
                            atr_val = row["ATR"]
                            entry_price = row["close"]
                            side = "sell" if "SELL" in action else "buy"
                            if side == "buy":
                                sl = entry_price - atr_val * 1.5
                                tp = entry_price + atr_val * 3
                            else:
                                sl = entry_price + atr_val * 1.5
                                tp = entry_price - atr_val * 3

                            from risk_manager import RiskManager
                            quantity = RiskManager.calculate_position_size(
                                entry_price, sl, self.portfolio.capital, side
                            )

                            # اگر حجم محاسبه‌شده صفر باشد (سرمایه ناکافی/ریسک نامعتبر)، معامله باز نمی‌شود
                            if quantity > 0:
                                self.trade_engine.open_trade(
                                    symbol=sym,
                                    side=side,
                                    entry_time=ts,
                                    entry_price=entry_price,
                                    stop_loss=sl,
                                    take_profit=tp,
                                    quantity=quantity,
                                    score=analysis["score"],
                                    confidence=decision["confidence"],
                                    entry_quality=decision["entry_quality"],
                                    trade_readiness=decision["trade_readiness"],
                                    risk_level=decision["summary"]["Risk Level"],
                                    market_bias=decision["summary"]["Market Bias"],
                                    reasons=analysis["reasons"],
                                    warnings=analysis["warnings"]
                                )

            equity = self.portfolio.capital + sum(
                self.trade_engine.calculate_unrealized_pnl(sym, ts, self.data[sym])
                for sym in self.trade_engine.open_trades
            )
            self.equity_curve.record(ts, equity)

        self.trade_engine.close_all(time_index[-1], self.data)

        print("Backtest finished. Generating report...")
        report = BacktestReport(
            trades=self.trade_engine.closed_trades,
            equity_curve=self.equity_curve,
            initial_capital=self.initial_capital,
            final_capital=self.portfolio.capital,
            output_dir=self.output_dir,
        )
        report.generate()
        report.print_summary()
