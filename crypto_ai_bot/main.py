"""
Crypto AI Bot v4
Main Trading Loop – 24/7 Automated Futures Trading
"""

import time
from scanner import MarketScanner
from report import ReportEngine
from risk_manager import RiskManager
from order_manager import OrderManager
from config import (
    TOP_RESULTS,
    SCAN_INTERVAL_MINUTES,
    MAX_OPEN_TRADES,
    TRAILING_STOP_ENABLED,
    TRAILING_STOP_ACTIVATION,
)


def main():
    print("Starting Crypto AI Bot...")
    scanner = MarketScanner()
    order_mgr = OrderManager()

    while True:
        print("\nScanning Market...")
        results = scanner.scan()

        if not results:
            print("No results.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        # انتخاب بهترین فرصت (بالاترین Trade Readiness) که Action قابل معامله باشد
        best_trade = None
        for res in results:
            if res.get("Action") in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"):
                best_trade = res
                break

        if best_trade is None:
            print("No tradable opportunity found.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        # بررسی وجود پوزیشن باز
        open_positions = order_mgr.check_open_positions()
        if len(open_positions) >= MAX_OPEN_TRADES:
            print("A position is already open. Waiting...")
            # اگر تریلینگ استاپ فعال است، آن را بررسی و اعمال کن
            if TRAILING_STOP_ENABLED and open_positions:
                # برای سادگی، روی اولین پوزیشن باز کار می‌کنیم
                pos = open_positions[0]
                # محاسبه درصد سود فعلی نسبت به TP اولیه (نیاز به ذخیره TP اولیه دارد)
                # چون TP را در response order ذخیره نکردیم، از best_trade فعلی استفاده نمی‌کنیم.
                # راه‌اندازی کامل تریلینگ نیاز به ذخیره اطلاعات معامله دارد.
                # به‌دلیل پیچیدگی، تریلینگ را به صورت داینامیک پیاده نمی‌کنیم.
                pass
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        # دریافت موجودی حساب
        balance = order_mgr.fetch_balance()
        if balance <= 0:
            print("Insufficient balance.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        symbol = best_trade["Symbol"]
        entry = best_trade["Price"]
        stop_loss = best_trade["StopLoss"]
        take_profit = best_trade["TakeProfit"]
        action = best_trade["Action"]

        # تعیین جهت معامله
        if "SELL" in action:
            side = "sell"
        else:
            side = "buy"

        # بررسی ریسک/ریوارد
        if not RiskManager.is_trade_valid(entry, stop_loss, take_profit, side):
            print("Risk/Reward too low. Skipping.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        # محاسبه حجم قرارداد
        quantity = RiskManager.calculate_position_size(entry, stop_loss, balance, side)
        if quantity <= 0:
            print("Invalid quantity.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        # اجرای معامله
        print(f"Opening {action} on {symbol}: Entry={entry}, SL={stop_loss}, TP={take_profit}, Qty={quantity}")
        order_result = order_mgr.place_market_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        print(f"Trade opened. Entry order: {order_result['entry_order']['id']}")

        # بعد از باز شدن معامله، مدتی صبر می‌کنیم تا پوزیشن باز شود
        time.sleep(5)

        # نظارت بر تریلینگ استاپ تا بسته شدن معامله
        if TRAILING_STOP_ENABLED:
            tp_target = take_profit
            entry_price = entry
            sl_order_id = order_result['sl_order']['id']
            current_sl = stop_loss
            while True:
                open_positions = order_mgr.check_open_positions(symbol)
                if not open_positions:
                    print("Position closed.")
                    break

                pos = open_positions[0]
                current_price = float(pos.get('markPrice', 0))
                # بررسی رسیدن به ۵۰٪ حد سود
                if side == "buy":
                    progress = (current_price - entry_price) / (tp_target - entry_price) if tp_target != entry_price else 0
                else:
                    progress = (entry_price - current_price) / (entry_price - tp_target) if entry_price != tp_target else 0

                if progress >= TRAILING_STOP_ACTIVATION and current_sl != entry_price:
                    # انتقال حد ضرر به نقطه ورود
                    print("Activating trailing stop: Moving SL to entry.")
                    new_sl_order = order_mgr.modify_stop_loss(
                        symbol=symbol,
                        sl_order_id=sl_order_id,
                        new_stop_price=entry_price,
                        quantity=quantity,
                    )
                    if new_sl_order:
                        sl_order_id = new_sl_order['id']
                        current_sl = entry_price

                time.sleep(10)   # بررسی هر ۱۰ ثانیه

        # بعد از بسته شدن، دوباره اسکن می‌شود
        time.sleep(SCAN_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
