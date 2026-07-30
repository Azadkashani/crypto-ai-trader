"""
Crypto AI Bot
Equity Curve Recorder & Exporter
"""

import pandas as pd


class EquityCurve:
    def __init__(self):
        self.times = []
        self.equities = []

    def record(self, time, equity):
        self.times.append(time)
        self.equities.append(equity)

    def to_dataframe(self):
        return pd.DataFrame({
            'time': self.times,
            'equity': self.equities
        })

    def save_csv(self, filename):
        self.to_dataframe().to_csv(filename, index=False)
