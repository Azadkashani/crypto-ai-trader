"""
Crypto AI Bot v5
Market Scanner
"""

from config import (
    SYMBOLS,
    USE_ALL_MARKETS,
    MAX_SYMBOLS,
    TOP_RESULTS,
)

from data import MarketData
from indicators import IndicatorEngine
from trend import TrendEngine
from scoring import ScoringEngine


class MarketScanner:

    def __init__(self):

        self.data = MarketData()

    def get_symbols(self):

        if USE_ALL_MARKETS:

            symbols = self.data.get_usdt_symbols()

            return symbols[:MAX_SYMBOLS]

        return SYMBOLS

    def scan(self):

        results = []

        symbols = self.get_symbols()

        print(f"Scanning {len(symbols)} symbols...\n")

        for symbol in symbols:

            try:

                df = self.data.get_ohlcv(symbol)

                df = IndicatorEngine.calculate(df)

                trend = TrendEngine.detect(df)

                strength = TrendEngine.strength(df)

                score, reasons = ScoringEngine.calculate(df)

                action = ScoringEngine.action(score)

                last = df.iloc[-1]

                support = df["low"].tail(50).min()

                resistance = df["high"].tail(50).max()

                results.append({

                    "Symbol": symbol,

                    "Price": round(last["close"], 4),

                    "Trend": trend,

                    "Strength": strength,

                    "RSI": round(last["RSI"], 2),

                    "Score": score,

                    "Action": action,

                    "Support": round(support, 4),

                    "Resistance": round(resistance, 4),

                    "Reasons": ", ".join(reasons)

                })

            except Exception as e:

                print(symbol, e)

        results = sorted(
            results,
            key=lambda x: x["Score"],
            reverse=True
        )

        return results[:TOP_RESULTS]
