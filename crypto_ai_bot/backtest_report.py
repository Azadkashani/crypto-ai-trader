"""
Crypto AI Bot
Backtest Report Generator
"""

import pandas as pd
import json
import os
from performance import Performance


class BacktestReport:
    def __init__(self, trades, equity_curve, initial_capital, final_capital, output_dir):
        self.trades = trades
        self.equity_curve = equity_curve
        self.initial_capital = initial_capital
        self.final_capital = final_capital
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self):
        # Trade History CSV
        trades_df = pd.DataFrame([t.__dict__ for t in self.trades])
        trades_df.to_csv(os.path.join(self.output_dir, "trade_history.csv"), index=False)

        # Equity Curve CSV
        self.equity_curve.save_csv(os.path.join(self.output_dir, "equity_curve.csv"))

        # Performance Summary JSON
        perf = Performance.calculate(self.trades, self.equity_curve,
                                     self.initial_capital, self.final_capital)
        with open(os.path.join(self.output_dir, "summary.json"), "w") as f:
            json.dump(perf, f, indent=4)

        self.perf = perf

    def print_summary(self):
        print("\n" + "=" * 50)
        print("BACKTEST RESULTS")
        print("=" * 50)
        for k, v in self.perf.items():
            print(f"{k}: {v}")
        print("=" * 50)
