"""
Crypto AI Bot
Risk Manager – Position Sizing & Dynamic Leverage
"""

from config import RISK_PER_TRADE


class RiskManager:
    @staticmethod
    def calculate_position_size(entry, stop_loss, account_balance, side="buy"):
        """
        محاسبه مقدار قرارداد (quantity) با ریسک دقیق ۱٪
        """
        risk_amount = account_balance * RISK_PER_TRADE

        if side in ("buy", "long"):
            sl_distance = entry - stop_loss
        else:  # sell, short
            sl_distance = stop_loss - entry

        if sl_distance <= 0:
            return 0

        quantity = risk_amount / sl_distance
        quantity = max(1, round(quantity, 4))
        return quantity

    @staticmethod
    def calculate_margin(entry, quantity, leverage):
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

    @staticmethod
    def suggest_leverage(entry, stop_loss, side, max_leverage=20):
        """
        پیشنهاد اهرم پویا بر اساس فاصلهٔ حد ضرر.
        فرمول: اهرم = 1 / (درصد فاصلهٔ حد ضرر × 1.5)
        هرچه حد ضرر نزدیک‌تر باشد، اهرم بالاتر می‌رود (تا سقف max_leverage).
        این کار ریسک ۱٪ را حفظ کرده و مارجین را بهینه می‌کند.
        """
        if entry <= 0:
            return 1
        if side in ("buy", "long"):
            sl_distance = entry - stop_loss
        else:
            sl_distance = stop_loss - entry

        if sl_distance <= 0:
            return 1

        sl_percent = sl_distance / entry
        # ضریب اطمینان 1.5 برای جلوگیری از لیکویید شدن در نوسانات
        dynamic_lev = int(1 / (sl_percent * 1.5))
        return min(max_leverage, max(1, dynamic_lev))
