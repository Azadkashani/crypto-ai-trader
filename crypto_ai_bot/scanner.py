"""
Crypto AI Bot v4
Market Scanner
"""

from config import SYMBOLS

from data import MarketData
from indicators import IndicatorEngine
from trend import TrendEngine
from scoring import ScoringEngine


class MarketScanner:

    def __init__(self):

        self.data = MarketData()

    def scan(self):

        results = []

        for symbol in SYMBOLS:

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

                print(f"{symbol} -> Error : {e}")

        results.sort(
            key=lambda x: x["Score"],
            reverse=True
        )

        return results
