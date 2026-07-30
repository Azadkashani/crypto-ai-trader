"""
Crypto AI Bot
Risk Manager – محاسبه Position Size و Leverage بر اساس ۱٪ ریسک
"""

from config import RISK_PER_TRADE, LEVERAGE


class RiskManager:
    @staticmethod
    def calculate_position_size(entry, stop_loss, account_balance, side="buy"):
        """
        محاسبه مقدار قرارداد (quantity) با ریسک دقیق ۱٪
        """
        risk_amount = account_balance * RISK_PER_TRADE   # مثلاً ۱۰۰ USDT

        if side in ("buy", "long"):
            sl_distance = entry - stop_loss
        else:  # sell, short
            sl_distance = stop_loss - entry

        if sl_distance <= 0:
            return 0  # حد ضرر نامعتبر

        # تعداد قراردادها = مقدار ریسک تقسیم بر فاصله حد ضرر (بر حسب دلار)
        quantity = risk_amount / sl_distance

        # بررسی حداقل حجم معاملاتی (در Gate.io معمولاً ۱ قرارداد)
        # می‌توان حداقل را ۱ در نظر گرفت
        quantity = max(1, round(quantity, 4))
        return quantity

    @staticmethod
    def calculate_margin(entry, quantity, leverage=LEVERAGE):
        """
        مارجین مورد نیاز برای پوزیشن ایزوله
        """
        return (entry * quantity) / leverage

    @staticmethod
    def is_trade_valid(entry, stop_loss, take_profit, side):
        """
        بررسی نسبت ریسک به ریوارد ≥ ۲
        """
        if side in ("buy", "long"):
            reward = take_profit - entry
            risk = entry - stop_loss
        else:
            reward = entry - take_profit
            risk = stop_loss - entry

        if risk <= 0:
            return False
        return (reward / risk) >= 2.0
