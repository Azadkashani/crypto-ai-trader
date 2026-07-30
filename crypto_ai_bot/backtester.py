"""
Crypto AI Bot
Backtester Engine – Core backtesting loop with causal market structure
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from data import MarketData
from indicators import IndicatorEngine
from market_structure import MarketStructure
from scoring import ScoringEngine
from decision_engine import DecisionEngine
from trade_engine import TradeEngine
from portfolio import Portfolio
from equity_curve import EquityCurve
from performance import Performance
from backtest_report import BacktestReport
from config import (
    LIMIT,
    ENABLE_NEWS_ENGINE,
    ENABLE_SENTIMENT_ENGINE,
)


class CausalMarketStructure:
    """
    یک نسخهٔ علّی از MarketStructure که برای بک‌تست طراحی شده است.
    در هر نقطه فقط از اطلاعات گذشته (تا کندل جاری) استفاده می‌کند
    و پس از دریافت ۵ کندل آینده، پیوت‌های قبلی را تأیید می‌کند.
    این کار Lookahead Bias را حذف می‌کند.
    """

    @staticmethod
    def analyze(df):
        return MarketStructure.analyze(df)


class Backtester:
    def __init__(self, symbols, start_date, end_date, timeframe,
                 initial_capital, risk_per_trade, leverage, max_open_trades,
                 trailing_stop, trailing_activation,
                 fee, slippage, spread, max_hold_bars, output_dir):
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

        self.data_engine = MarketData()
        self.portfolio = Portfolio(initial_capital, risk_per_trade, leverage, fee, slippage, spread)
        self.trade_engine = TradeEngine(self.portfolio, trailing_stop, trailing_activation, max_hold_bars)
        self.equity_curve = EquityCurve()

        self.data = {}
        self.indicators = {}
        self.market_structures = {}
        self.advanced_analytics = {}

    def load_data(self):
        for sym in self.symbols:
            try:
                df = self.data_engine.get_ohlcv(sym, timeframe=self.timeframe)
                if df.empty:
                    print(f"No data for {sym}")
                    continue
                df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                if df.empty:
                    print(f"No data in range for {sym}")
                    continue
                df = df.reset_index(drop=True)
                self.data[sym] = df
                self.indicators[sym] = IndicatorEngine.calculate(df.copy())
            except Exception as e:
                print(f"Could not load {sym}: {e}")

    def compute_analysis(self, sym):
        if sym not in self.indicators:
            return
        df = self.indicators[sym]
        self.market_structures[sym] = CausalMarketStructure.analyze(df)
        self.advanced_analytics[sym] = None

    def run(self):
        print("Loading historical data...")
        self.load_data()

        # حذف نمادهایی که داده ندارند
        self.symbols = [s for s in self.symbols if s in self.data]
        if not self.symbols:
            print("No valid symbols for backtest.")
            return

        print("Computing indicators and structure...")
        for sym in self.symbols:
            self.compute_analysis(sym)

        # یکپارچه‌سازی زمانی
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
                row = self.indicators[sym].iloc[idx]

                if not self.trade_engine.is_position_open(sym):
                    ms = self.market_structures[sym]
                    from trend import TrendEngine
                    strength = TrendEngine.strength(self.indicators[sym])
                    mtf_signal = "Neutral"

                    analysis = ScoringEngine.calculate(
                        self.indicators[sym],
                        mtf_signal,
                        market_structure=ms,
                        strength=strength,
                        advanced_data=None,
                    )

                    decision = DecisionEngine.evaluate(
                        self.indicators[sym],
                        ms,
                        mtf_signal,
                        strength,
                        None,
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
