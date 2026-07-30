"""
Crypto AI Bot v4
Main Trading Loop – 24/7 Automated Futures Trading
"""

import time
from scanner import MarketScanner
from report import ReportEngine
from config import (
    API_KEY,
    API_SECRET,
    SCAN_INTERVAL_MINUTES,
    MAX_OPEN_TRADES,
    TRAILING_STOP_ENABLED,
    TRAILING_STOP_ACTIVATION,
)

# فعال بودن معاملات فقط در صورتی که هر دو کلید تنظیم شده باشند
TRADING_ENABLED = bool(API_KEY and API_SECRET)
if TRADING_ENABLED:
    from risk_manager import RiskManager
    from order_manager import OrderManager


def main():
    print("Starting Crypto AI Bot...")
    scanner = MarketScanner()
    order_mgr = None

    if TRADING_ENABLED:
        order_mgr = OrderManager()
        print("Trading mode: ENABLED")
    else:
        print("Trading mode: DISABLED (API keys not set)")
        print("Running in scan-only mode...")

    while True:
        print("\nScanning Market...")
        results = scanner.scan()

        if not results:
            print("No results.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        # اگر حالت معاملاتی فعال نیست، فقط گزارش بده و دوباره اسکن کن
        if not TRADING_ENABLED:
            ReportEngine.show(results)
            print(f"\nNext scan in {SCAN_INTERVAL_MINUTES} minutes...")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        # ========== بخش معاملات (فقط در صورت وجود کلید) ==========
        best_trade = None
        for res in results:
            if res.get("Action") in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"):
                best_trade = res
                break

        if best_trade is None:
            print("No tradable opportunity found.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        open_positions = order_mgr.check_open_positions()
        if len(open_positions) >= MAX_OPEN_TRADES:
            print("A position is already open. Waiting...")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

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

        side = "sell" if "SELL" in action else "buy"

        if not RiskManager.is_trade_valid(entry, stop_loss, take_profit, side):
            print("Risk/Reward too low. Skipping.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        quantity = RiskManager.calculate_position_size(entry, stop_loss, balance, side)
        if quantity <= 0:
            print("Invalid quantity.")
            time.sleep(SCAN_INTERVAL_MINUTES * 60)
            continue

        print(f"Opening {action} on {symbol}: Entry={entry}, SL={stop_loss}, TP={take_profit}, Qty={quantity}")
        order_result = order_mgr.place_market_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            entry_price=entry,
        )
        print(f"Trade opened. Entry order: {order_result['entry_order']['id']}")

        if TRAILING_STOP_ENABLED:
            tp_target = take_profit
            entry_price = entry
            sl_order_id = order_result['sl_order']['id']
            current_sl = stop_loss
            print("Monitoring position for trailing stop...")
            while True:
                open_positions = order_mgr.check_open_positions(symbol)
                if not open_positions:
                    print("Position closed.")
                    break

                pos = open_positions[0]
                current_price = float(pos.get('markPrice', 0))

                if side == "buy":
                    progress = (current_price - entry_price) / (tp_target - entry_price) if tp_target != entry_price else 0
                else:
                    progress = (entry_price - current_price) / (entry_price - tp_target) if entry_price != tp_target else 0

                if progress >= TRAILING_STOP_ACTIVATION and current_sl != entry_price:
                    print(f"Activating trailing stop (progress={progress:.2f}): Moving SL to entry.")
                    new_sl_order = order_mgr.modify_stop_loss(
                        symbol=symbol,
                        sl_order_id=sl_order_id,
                        new_stop_price=entry_price,
                        quantity=quantity,
                    )
                    if new_sl_order:
                        sl_order_id = new_sl_order['id']
                        current_sl = entry_price

                time.sleep(10)

        time.sleep(SCAN_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main()
