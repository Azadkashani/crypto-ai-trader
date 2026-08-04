"""
Crypto AI Bot v1.2
Risk Manager – Adaptive Position Sizing, Dynamic Leverage
"""

from config import (
    RISK_PER_TRADE, LEVERAGE as MAX_LEVERAGE,
    MIN_POSITION_RISK, MAX_POSITION_RISK, ENABLE_ADAPTIVE_POSITION_SIZING
)

class RiskManager:
    @staticmethod
    def calculate_position_size(entry, stop_loss, account_balance, side="buy", risk_pct=RISK_PER_TRADE):
        risk_amount = account_balance * risk_pct
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
        if entry <= 0: return 1
        if side in ("buy", "long"):
            sl_distance = entry - stop_loss
        else:
            sl_distance = stop_loss - entry
        if sl_distance <= 0: return 1
        stop_loss_pct = sl_distance / entry
        if stop_loss_pct == 0: return 1
        if stop_loss_pct < RISK_PER_TRADE:
            leverage = RISK_PER_TRADE / stop_loss_pct
            return min(max_leverage, max(1, int(leverage)))
        else:
            return 1

    @staticmethod
    def adaptive_risk_pct(atr, adx, market_structure_quality, confidence, trade_readiness,
                          mtf_agreement, volume_z, news_score, sentiment_score, macro_risk):
        if not ENABLE_ADAPTIVE_POSITION_SIZING:
            return RISK_PER_TRADE
        score = 0.5
        if atr > 0.03: score -= 0.1
        elif atr < 0.01: score += 0.1
        if adx >= 40: score += 0.15
        elif adx >= 25: score += 0.1
        elif adx < 15: score -= 0.1
        score += market_structure_quality * 0.1
        score += (confidence / 100.0 - 0.5) * 0.2
        score += (trade_readiness / 100.0 - 0.5) * 0.2
        if mtf_agreement > 0.8: score += 0.1
        elif mtf_agreement < 0.3: score -= 0.1
        if volume_z > 1.0: score += 0.1
        elif volume_z < -1.0: score -= 0.1
        if news_score > 5: score += 0.1
        elif news_score < -5: score -= 0.1
        if sentiment_score > 5: score += 0.05
        elif sentiment_score < -5: score -= 0.05
        if macro_risk: score -= 0.15
        score = max(0.0, min(1.0, score))
        risk_pct = MIN_POSITION_RISK + (MAX_POSITION_RISK - MIN_POSITION_RISK) * score
        return round(risk_pct, 4)
