"""
Crypto AI Bot v1.2
Expected Value Calculator – Multi-target, Probability-based
"""

from config import MIN_RISK_REWARD

class ExpectedValue:
    @staticmethod
    def calculate(targets, entry, stop_loss, confidence, trade_readiness,
                  trend_strength, news_score, sentiment_score, volatility, volume_z):
        """
        targets: list of dicts with 'price' and 'probability'
        """
        if not targets or stop_loss is None or entry == stop_loss:
            return 0.0

        risk = abs(entry - stop_loss)
        total_prob = 0.0
        weighted_reward = 0.0

        for t in targets:
            prob = t.get("probability", 0.0)
            reward = abs(t["price"] - entry)
            total_prob += prob
            weighted_reward += prob * reward

        if total_prob > 1.0:
            total_prob = 1.0

        if total_prob == 0.0:
            return 0.0

        avg_reward = weighted_reward / total_prob
        avg_rr = avg_reward / risk if risk > 0 else 0

        # Adjust win rate based on confidence, readiness, trend, etc.
        win_rate = total_prob
        win_rate += (confidence / 100.0 - 0.5) * 0.1
        win_rate += (trade_readiness / 100.0 - 0.5) * 0.1
        if trend_strength == "Very Strong": win_rate += 0.05
        elif trend_strength == "Strong": win_rate += 0.03
        elif trend_strength == "Weak": win_rate -= 0.05
        if news_score > 5: win_rate += 0.02
        elif news_score < -5: win_rate -= 0.02
        if sentiment_score > 5: win_rate += 0.02
        elif sentiment_score < -5: win_rate -= 0.02
        if volatility == "High Volatility": win_rate -= 0.03
        elif volatility == "Low Volatility": win_rate += 0.02
        if volume_z > 1.0: win_rate += 0.02
        elif volume_z < -1.0: win_rate -= 0.02

        win_rate = max(0.05, min(0.9, win_rate))
        loss_rate = 1.0 - win_rate

        ev = (win_rate * avg_rr) - (loss_rate * 1.0)
        return round(ev, 2)
