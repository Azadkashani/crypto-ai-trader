"""
Crypto AI Bot v1.2
Expected Value Calculator – Realistic Parameters
"""

from config import MIN_RISK_REWARD

class ExpectedValue:
    @staticmethod
    def calculate(rr, confidence, trade_readiness, trend_strength,
                  news_score, sentiment_score, volatility, volume_z, historical_win_rate=0.55):
        wr = historical_win_rate
        wr += (confidence / 100.0 - 0.5) * 0.2
        wr += (trade_readiness / 100.0 - 0.5) * 0.2
        if trend_strength == "Very Strong": wr += 0.08
        elif trend_strength == "Strong": wr += 0.04
        elif trend_strength == "Weak": wr -= 0.08
        if news_score > 5: wr += 0.03
        elif news_score < -5: wr -= 0.03
        if sentiment_score > 5: wr += 0.03
        elif sentiment_score < -5: wr -= 0.03
        if volatility == "High Volatility": wr -= 0.05
        elif volatility == "Low Volatility": wr += 0.03
        if volume_z > 1.0: wr += 0.03
        elif volume_z < -1.0: wr -= 0.03
        wr = max(0.1, min(0.85, wr))
        lr = 1.0 - wr

        if rr < MIN_RISK_REWARD:
            return 0.0
        reward = rr
        risk = 1.0
        ev = (wr * reward) - (lr * risk)
        return round(ev, 2)
