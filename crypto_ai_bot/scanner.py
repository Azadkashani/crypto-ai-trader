"""
Crypto AI Bot v5.3
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


                analysis = ScoringEngine.calculate(df)


                score = analysis["score"]

                confidence = analysis["confidence"]

                breakout = analysis["breakout"]

                reasons = analysis["reasons"]

                warnings = analysis["warnings"]


                action = ScoringEngine.action(
                    score,
                    breakout
                )


                last = df.iloc[-1]


                support = round(
                    df["low"].tail(50).min(),
                    4
                )

                resistance = round(
                    df["high"].tail(50).max(),
                    4
                )


                atr = float(last["ATR"])


                entry = round(
                    last["close"],
                    4
                )


                stop_loss = round(
                    entry - (atr * 1.5),
                    4
                )


                take_profit = round(
                    entry + (atr * 3),
                    4
                )


                results.append({

                    "Symbol": symbol,

                    "Price": entry,

                    "Trend": trend,

                    "Strength": strength,

                    "Confidence": confidence,

                    "RSI": round(
                        last["RSI"],
                        2
                    ),

                    "Score": score,

                    "Action": action,

                    "Support": support,

                    "Resistance": resistance,

                    "Entry": entry,

                    "StopLoss": stop_loss,

                    "TakeProfit": take_profit,

                    "Breakout": breakout,

                    "Reasons": ", ".join(reasons),

                    "Warnings": ", ".join(warnings)

                })


            except Exception as e:

                print(f"{symbol} : {e}")


        results = sorted(
            results,
            key=lambda x: x["Score"],
            reverse=True
        )


        return results[:TOP_RESULTS]
