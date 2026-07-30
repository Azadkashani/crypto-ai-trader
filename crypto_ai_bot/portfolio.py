"""
Crypto AI Bot
Portfolio Manager – Capital tracking, fees, slippage, and spread
"""

class Portfolio:
    def __init__(self, initial_capital, risk_per_trade, leverage,
                 fee, slippage, spread):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.leverage = leverage
        self.fee = fee          # e.g., 0.0004
        self.slippage = slippage  # e.g., 0.0005
        self.spread = spread    # e.g., 0.0002
