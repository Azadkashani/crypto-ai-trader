"""
Crypto AI Bot
Backtest Runner – Multi-source + Mock mode
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
                        help='Symbol(s) to test')
    parser.add_argument('--start', type=str, default='2024-01-01',
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default='2024-06-30',
                        help='End date (YYYY-MM-DD)')
    parser.add_argument('--initial-capital', type=float, default=10000)
    parser.add_argument('--timeframe', type=str, default=TIMEFRAME)
    parser.add_argument('--exchange', type=str, default='kucoin')
    parser.add_argument('--risk-per-trade', type=float, default=RISK_PER_TRADE)
    parser.add_argument('--leverage', type=int, default=LEVERAGE)
    parser.add_argument('--max-open-trades', type=int, default=MAX_OPEN_TRADES)
    parser.add_argument('--trailing-stop', type=bool, default=TRAILING_STOP_ENABLED)
    parser.add_argument('--trailing-activation', type=float, default=TRAILING_STOP_ACTIVATION)
    parser.add_argument('--fee', type=float, default=0.0004)
    parser.add_argument('--slippage', type=float, default=0.0005)
    parser.add_argument('--spread', type=float, default=0.0002)
    parser.add_argument('--max-hold-bars', type=int, default=200)
    parser.add_argument('--output-dir', type=str, default='backtest_results')
    parser.add_argument('--mock', action='store_true', help='Use mock data')

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
        use_mock=args.mock,
    )
    bt.run()


if __name__ == "__main__":
    main()
