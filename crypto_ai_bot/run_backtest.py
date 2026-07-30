"""
Crypto AI Bot
Backtest Runner – Entry point for backtesting (with exchange selection)
"""

import argparse
from backtester import Backtester
from config import (
    SYMBOLS,
    TIMEFRAME,
    RISK_PER_TRADE,
    LEVERAGE,
    TRAILING_STOP_ENABLED,
    TRAILING_STOP_ACTIVATION,
    MAX_OPEN_TRADES,
)


def main():
    parser = argparse.ArgumentParser(description='Crypto AI Bot Backtester')
    parser.add_argument('--symbols', nargs='+', default=SYMBOLS[:5],
                        help='Symbol(s) to test (e.g. BTC/USDT ETH/USDT)')
    parser.add_argument('--start', type=str, required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True,
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--initial-capital', type=float, default=10000,
                        help='Initial capital in USDT')
    parser.add_argument('--timeframe', type=str, default=TIMEFRAME,
                        help='Timeframe (e.g., 1h, 4h)')
    parser.add_argument('--exchange', type=str, default='binance',
                        help='Exchange to fetch data from (binance, gate)')
    parser.add_argument('--risk-per-trade', type=float, default=RISK_PER_TRADE,
                        help='Risk per trade (0.01 = 1%)')
    parser.add_argument('--leverage', type=int, default=LEVERAGE,
                        help='Leverage')
    parser.add_argument('--max-open-trades', type=int, default=MAX_OPEN_TRADES,
                        help='Maximum concurrent trades')
    parser.add_argument('--trailing-stop', type=bool, default=TRAILING_STOP_ENABLED,
                        help='Enable trailing stop')
    parser.add_argument('--trailing-activation', type=float, default=TRAILING_STOP_ACTIVATION,
                        help='Trailing stop activation (0.5 = 50%)')
    parser.add_argument('--fee', type=float, default=0.0004,
                        help='Exchange fee (0.0004 = 0.04%)')
    parser.add_argument('--slippage', type=float, default=0.0005,
                        help='Slippage (0.0005 = 0.05%)')
    parser.add_argument('--spread', type=float, default=0.0002,
                        help='Bid-ask spread (0.0002 = 0.02%)')
    parser.add_argument('--max-hold-bars', type=int, default=200,
                        help='Max holding bars (time-based exit)')
    parser.add_argument('--output-dir', type=str, default='backtest_results',
                        help='Directory for output files')

    args = parser.parse_args()

    bt = Backtester(
        symbols=args.symbols,
        start_date=args.start,
        end_date=args.end,
        timeframe=args.timeframe,
        initial_capital=args.initial_capital,
        risk_per_trade=args.risk_per_trade,
        leverage=args.leverage,
        max_open_trades=args.max_open_trades,
        trailing_stop=args.trailing_stop,
        trailing_activation=args.trailing_activation,
        fee=args.fee,
        slippage=args.slippage,
        spread=args.spread,
        max_hold_bars=args.max_hold_bars,
        output_dir=args.output_dir,
        exchange_name=args.exchange,
    )
    bt.run()


if __name__ == "__main__":
    main()
