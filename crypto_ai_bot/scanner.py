"""
Crypto AI Bot v5.7
Market Scanner + Multi Timeframe Engine
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

from mtf_engine import MTFEngine
from timeframe import TIMEFRAMES



class MarketScanner:


    def __init__(self):

        self.data = MarketData()



    def get_symbols(self):

        if USE_ALL_MARKETS:

            symbols = self.data.get_usdt_symbols()

            return symbols[:MAX_SYMBOLS]


        return SYMBOLS



    def analyze_mtf(self, symbol):

        """
        Multi Timeframe Analysis

        Example:
        15m -> Bullish
        1h  -> Bullish
        4h  -> Bearish
        """

        mtf_results = {}


        for tf in TIMEFRAMES:


            try:

                df = self.data.get_ohlcv(
    symbol,
    timeframe=tf
)


                df = IndicatorEngine.calculate(df)


                trend = TrendEngine.detect(df)


                mtf_results[tf] = trend


            except Exception:


                mtf_results[tf] = "Neutral"



        mtf_signal = MTFEngine.analyze(
            mtf_results
        )


        return (
            mtf_signal,
            mtf_results
        )





    def scan(self):


        results = []


        symbols = self.get_symbols()


        print(
            f"Scanning {len(symbols)} symbols...\n"
        )



        for symbol in symbols:


            try:


                df = self.data.get_ohlcv(symbol)


                df = IndicatorEngine.calculate(df)



                trend = TrendEngine.detect(df)


                strength = TrendEngine.strength(df)

                # ==============================
                # MTF
                # ==============================

                mtf_signal, mtf_details = self.analyze_mtf(
                    symbol
                )

                analysis = ScoringEngine.calculate(
    df,
    mtf_signal
)



                base_score = analysis["base_score"]

                mtf_bonus = analysis["mtf_bonus"]

                score = analysis["score"]

                confidence = analysis["confidence"]


                breakout = analysis["breakout"]


                reasons = analysis["reasons"]


                warnings = analysis["warnings"]



                action = ScoringEngine.action(
                    score,
                    breakout
                )

                # ==============================
                # Base Score Filter
                # ==============================

                if action in [
                    "BUY",
                    "BUY BREAKOUT"
                ] and base_score < 75:

                    action = "WATCH"

                    warnings.append(
                        "Low Base Score"
                    )

                



                # ==============================
                # Trend Filter
                # ==============================


                if trend == "Sideways":


                    if action in [
                        "BUY",
                        "BUY BREAKOUT"
                    ]:


                        action = "WATCH"


                        warnings.append(
                            "Sideways Trend"
                        )



                if trend == "Bearish":


                    action = "NO TRADE"


                    warnings.append(
                        "Bearish Trend"
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



                atr = float(
                    last["ATR"]
                )



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


                    "MTF_Signal": mtf_signal,


                    "MTF_Details": mtf_details,


                    "Confidence": confidence,


                    "RSI": round(
                        last["RSI"],
                        2
                    ),

                    "Base Score": base_score,

                    "MTF Bonus": mtf_bonus,
                    
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


                print(
                    f"{symbol} : {e}"
                )



        results = sorted(
            results,
            key=lambda x: x["Score"],
            reverse=True
        )



        return results[:TOP_RESULTS]
