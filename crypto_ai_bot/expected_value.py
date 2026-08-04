"""
Crypto AI Bot v1.2
Expected Value Calculator
"""

from config import MIN_RISK_REWARD, ENABLE_EXPECTED_VALUE

class ExpectedValue:
    @staticmethod
    def calculate(rr, confidence, trade_readiness, trend_strength,
                  news_score, sentiment_score, volatility, volume_z, historical_win_rate=0.55):
        """
        محاسبهٔ Expected Value به‌صورت مضربی از Risk.
        historical_win_rate می‌تواند از بک‌تست ذخیره شود.
        """
        if not ENABLE_EXPECTED_VALUE:
            return 0.0

        # تنظیم Win Rate بر اساس کیفیت سیگنال
        adjusted_win_rate = historical_win_rate
        # Confidence و Readiness
        adjusted_win_rate += (confidence / 100.0 - 0.5) * 0.2
        adjusted_win_rate += (trade_readiness / 100.0 - 0.5) * 0.2
        # روند قوی
        if trend_strength == "Very Strong":
            adjusted_win_rate += 0.1
        elif trend_strength == "Strong":
            adjusted_win_rate += 0.05
        elif trend_strength == "Weak":
            adjusted_win_rate -= 0.1
        # News و Sentiment
        if news_score > 5:
            adjusted_win_rate += 0.05
        elif news_score < -5:
            adjusted_win_rate -= 0.05
        if sentiment_score > 5:
            adjusted_win_rate += 0.05
        elif sentiment_score < -5:
            adjusted_win_rate -= 0.05
        # نوسان بالا → کاهش win rate
        if volatility == "High Volatility":
            adjusted_win_rate -= 0.1
        elif volatility == "Low Volatility":
            adjusted_win_rate += 0.05
        # حجم بالا
        if volume_z > 1.0:
            adjusted_win_rate += 0.05
        elif volume_z < -1.0:
            adjusted_win_rate -= 0.05

        # محدود کردن Win Rate
        adjusted_win_rate = max(0.1, min(0.9, adjusted_win_rate))
        loss_rate = 1.0 - adjusted_win_rate

        # Reward و Risk بر اساس R:R
        # اگر RR کمتر از حداقل است، EV=0
        if rr < MIN_RISK_REWARD:
            return 0.0

        # Reward به ازای هر واحد Risk (RR)
        reward = rr
        risk = 1.0

        ev = (adjusted_win_rate * reward) - (loss_rate * risk)
        return round(ev, 2)
