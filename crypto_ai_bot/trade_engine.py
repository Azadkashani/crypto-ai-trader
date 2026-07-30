"""
Crypto AI Bot
Trade Engine – Simulates trade entry/exit, trailing stop, and position management
"""

import pandas as pd


class Trade:
    def __init__(self, symbol, side, entry_time, entry_price, stop_loss, take_profit,
                 quantity, score, confidence, entry_quality, trade_readiness,
                 risk_level, market_bias, reasons, warnings):
        self.symbol = symbol
        self.side = side
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.quantity = quantity
        self.exit_time = None
        self.exit_price = None
        self.exit_reason = None
        self.pnl = 0.0
        self.pnl_pct = 0.0
        self.holding_bars = 0

        # metadata
        self.score = score
        self.confidence = confidence
        self.entry_quality = entry_quality
        self.trade_readiness = trade_readiness
        self.risk_level = risk_level
        self.market_bias = market_bias
        self.reasons = reasons
        self.warnings = warnings

    def update_exit(self, exit_time, exit_price, reason):
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.exit_reason = reason
        if self.side == "buy":
            self.pnl = (exit_price - self.entry_price) * self.quantity
            self.pnl_pct = (exit_price / self.entry_price - 1) * 100
        else:
            self.pnl = (self.entry_price - exit_price) * self.quantity
            self.pnl_pct = (self.entry_price / exit_price - 1) * 100
        self.holding_bars = (exit_time - self.entry_time).total_seconds() / 3600  # hours


class TradeEngine:
    def __init__(self, portfolio, trailing_stop_enabled, trailing_activation, max_hold_bars):
        self.portfolio = portfolio
        self.trailing_stop_enabled = trailing_stop_enabled
        self.trailing_activation = trailing_activation
        self.max_hold_bars = max_hold_bars
        self.open_trades = {}
        self.closed_trades = []

    def is_position_open(self, symbol):
        return symbol in self.open_trades

    def open_trade(self, symbol, side, entry_time, entry_price, stop_loss, take_profit,
                   quantity, **metadata):
        # کسر کارمزد ورود
        entry_fee = entry_price * quantity * self.portfolio.fee
        self.portfolio.capital -= entry_fee

        trade = Trade(symbol, side, entry_time, entry_price, stop_loss, take_profit,
                      quantity, **metadata)
        self.open_trades[symbol] = trade

    def update(self, current_time, data_dict, indicators_dict, market_structures):
        """بررسی خروج پوزیشن‌های باز بر اساس کندل جاری"""
        for sym, trade in list(self.open_trades.items()):
            df = data_dict[sym]
            row = df[df['time'] == current_time]
            if len(row) == 0:
                continue
            candle = row.iloc[0]
            high = candle["high"]
            low = candle["low"]
            close = candle["close"]

            exit_reason = None
            exit_price = None

            # 1. Stop Loss
            if trade.side == "buy":
                if low <= trade.stop_loss:
                    exit_reason = "Stop Loss"
                    exit_price = trade.stop_loss
            else:  # sell
                if high >= trade.stop_loss:
                    exit_reason = "Stop Loss"
                    exit_price = trade.stop_loss

            # 2. Take Profit
            if exit_reason is None:
                if trade.side == "buy":
                    if high >= trade.take_profit:
                        exit_reason = "Take Profit"
                        exit_price = trade.take_profit
                else:
                    if low <= trade.take_profit:
                        exit_reason = "Take Profit"
                        exit_price = trade.take_profit

            # 3. Trailing Stop (فعال‌سازی و حرکت)
            if self.trailing_stop_enabled and trade.side == "buy":
                if close >= trade.entry_price + self.trailing_activation * (trade.take_profit - trade.entry_price):
                    # به‌روزرسانی حد ضرر به نقطه ورود (Breakeven)
                    trade.stop_loss = max(trade.stop_loss, trade.entry_price)
            elif self.trailing_stop_enabled and trade.side == "sell":
                if close <= trade.entry_price - self.trailing_activation * (trade.entry_price - trade.take_profit):
                    trade.stop_loss = min(trade.stop_loss, trade.entry_price)

            # 4. Max Holding Bars
            if exit_reason is None:
                bars_held = (current_time - trade.entry_time).total_seconds() / 3600
                if bars_held >= self.max_hold_bars:
                    exit_reason = "Max Holding Time"
                    exit_price = close

            # 5. Reverse Signal (اختیاری – فعلاً پیاده‌سازی نشده)

            if exit_reason:
                trade.update_exit(current_time, exit_price, exit_reason)
                # کارمزد خروج
                exit_fee = exit_price * trade.quantity * self.portfolio.fee
                self.portfolio.capital += trade.pnl - exit_fee
                self.closed_trades.append(trade)
                del self.open_trades[sym]

    def close_all(self, final_time, data_dict):
        """بستن تمام معاملات باز در پایان بک‌تست"""
        for sym, trade in self.open_trades.items():
            df = data_dict[sym]
            last_price = df.iloc[-1]["close"]
            trade.update_exit(final_time, last_price, "End of Backtest")
            exit_fee = last_price * trade.quantity * self.portfolio.fee
            self.portfolio.capital += trade.pnl - exit_fee
            self.closed_trades.append(trade)
        self.open_trades.clear()

    def calculate_unrealized_pnl(self, symbol, current_time, df):
        """محاسبه PnL تحقق‌نیافته (برای equity curve)"""
        if symbol not in self.open_trades:
            return 0.0
        trade = self.open_trades[symbol]
        row = df[df['time'] == current_time]
        if len(row) == 0:
            return 0.0
        price = row.iloc[0]["close"]
        if trade.side == "buy":
            return (price - trade.entry_price) * trade.quantity
        else:
            return (trade.entry_price - price) * trade.quantity
