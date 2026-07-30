"""
Crypto AI Bot
Performance Metrics Calculator
"""

import numpy as np
import pandas as pd

class Performance:
    @staticmethod
    def calculate(trades, equity_curve, initial_capital, final_capital):
        df_trades = pd.DataFrame([t.__dict__ for t in trades])
        if df_trades.empty:
            return {}

        total_trades = len(df_trades)
        winning_trades = len(df_trades[df_trades['pnl'] > 0])
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades * 100

        gross_profit = df_trades[df_trades['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df_trades[df_trades['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')

        net_profit = gross_profit - gross_loss
        avg_win = df_trades[df_trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = df_trades[df_trades['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        avg_holding = df_trades['holding_bars'].mean()

        # Drawdown
        equity_series = equity_curve.to_dataframe()['equity']
        peak = equity_series.expanding().max()
        drawdown = (peak - equity_series) / peak
        max_drawdown = drawdown.max() * 100

        # Expectancy
        expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * abs(avg_loss))

        # Sharpe Ratio (daily, assuming each bar = 1h -> 24 bars/day)
        returns = equity_series.pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252 * 24) if returns.std() != 0 else 0

        # Sortino Ratio
        downside = returns[returns < 0].std()
        sortino = (returns.mean() / downside) * np.sqrt(252 * 24) if downside != 0 else 0

        # Calmar Ratio
        calmar = (returns.mean() * 252 * 24) / (max_drawdown / 100) if max_drawdown != 0 else 0

        # Recovery Factor
        recovery_factor = net_profit / (max_drawdown / 100 * initial_capital) if max_drawdown != 0 else 0

        # Consecutive
        pnl_signs = df_trades['pnl'].apply(lambda x: 1 if x > 0 else -1).tolist()
        max_cons_wins = Performance._max_consecutive(pnl_signs, 1)
        max_cons_losses = Performance._max_consecutive(pnl_signs, -1)

        return {
            "Total Trades": total_trades,
            "Winning Trades": winning_trades,
            "Losing Trades": losing_trades,
            "Win Rate %": round(win_rate, 2),
            "Profit Factor": round(profit_factor, 2),
            "Gross Profit": round(gross_profit, 2),
            "Gross Loss": round(gross_loss, 2),
            "Net Profit": round(net_profit, 2),
            "Average Win": round(avg_win, 2),
            "Average Loss": round(avg_loss, 2),
            "Average Holding (hours)": round(avg_holding, 2),
            "Expectancy": round(expectancy, 2),
            "Max Drawdown %": round(max_drawdown, 2),
            "Max Consecutive Wins": max_cons_wins,
            "Max Consecutive Losses": max_cons_losses,
            "Sharpe Ratio": round(sharpe, 2),
            "Sortino Ratio": round(sortino, 2),
            "Calmar Ratio": round(calmar, 2),
            "Recovery Factor": round(recovery_factor, 2),
            "Return %": round((final_capital / initial_capital - 1) * 100, 2),
            "Final Balance": round(final_capital, 2),
        }

    @staticmethod
    def _max_consecutive(sequence, target):
        max_streak = 0
        current_streak = 0
        for s in sequence:
            if s == target:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        return max_streak
