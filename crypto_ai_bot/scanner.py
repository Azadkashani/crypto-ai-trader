"""
Crypto AI Bot v5.6
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

                # دریافت دیتا

                df = self.data.get_ohlcv(symbol)


                # اندیکاتورها

                df = IndicatorEngine.calculate(df)



                # تحلیل روند

                trend = TrendEngine.detect(df)

                strength = TrendEngine.strength(df)



                # امتیازدهی

                analysis = ScoringEngine.calculate(df)


                score = analysis["score"]

                confidence = analysis["confidence"]

                reasons = analysis["reasons"]

                breakout = analysis["breakout"]



                # اکشن نهایی

                action = ScoringEngine.action(
                    score,
                    breakout
                )



                last = df.iloc[-1]



                # سطوح

                support = round(
                    df["low"]
                    .tail(50)
                    .min(),
                    4
                )


                resistance = round(
                    df["high"]
                    .tail(50)
                    .max(),
                    4
                )



                atr = float(last["ATR"])


                entry = round(
                    float(last["close"]),
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



                adx = round(
                    float(last.get("ADX",0)),
                    2
                )



                results.append({

                    "Symbol": symbol,

                    "Price": entry,

                    "Trend": trend,

                    "Strength": strength,

                    "ADX": adx,

                    "Confidence": confidence,

                    "RSI": round(
                        float(last["RSI"]),
                        2
                    ),

                    "Score": score,

                    "Breakout": breakout,

                    "Action": action,


                    "Support": support,

                    "Resistance": resistance,


                    "Entry": entry,

                    "StopLoss": stop_loss,

                    "TakeProfit": take_profit,


                    "Reasons":
                        ", ".join(reasons)

                })



            except Exception as e:

                print(
                    f"{symbol} : {e}"
                )



        results = sorted(
            results,
            key=lambda x:x["Score"],
            reverse=True
        )


        return results[:TOP_RESULTS]
