"""
Crypto AI Bot v1.1
Risk Manager – Position Sizing & Dynamic Leverage (1% Risk Rule, no minimum qty)
"""

from config import RISK_PER_TRADE, LEVERAGE as MAX_LEVERAGE


class RiskManager:
    @staticmethod
    def calculate_position_size(entry, stop_loss, account_balance, side="buy"):
        risk_amount = account_balance * RISK_PER_TRADE
        if side in ("buy", "long"):
            sl_distance = entry - stop_loss
        else:
            sl_distance = stop_loss - entry
        if sl_distance <= 0:
            return 0.0
        quantity = risk_amount / sl_distance
        return round(quantity, 8)

    @staticmethod
    def calculate_margin(entry, quantity, leverage):
        return (entry * quantity) / leverage

    @staticmethod
    def is_trade_valid(entry, stop_loss, take_profit, side):
        if side in ("buy", "long"):
            reward = take_profit - entry
            risk = entry - stop_loss
        else:
            reward = entry - take_profit
            risk = stop_loss - entry
        if risk <= 0:
            return False
        return (reward / risk) >= 2.0

    @staticmethod
    def suggest_leverage(entry, stop_loss, side, max_leverage=MAX_LEVERAGE):
        if entry <= 0:
            return 1
        if side in ("buy", "long"):
            sl_distance = entry - stop_loss
        else:
            sl_distance = stop_loss - entry
        if sl_distance <= 0:
            return 1
        stop_loss_pct = sl_distance / entry
        if stop_loss_pct == 0:
            return 1
        if stop_loss_pct < RISK_PER_TRADE:
            leverage = RISK_PER_TRADE / stop_loss_pct
            return min(max_leverage, max(1, int(leverage)))
        else:
            return 1
