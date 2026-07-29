"""
Crypto AI Bot v5.7
Market Scanner + Multi Timeframe Engine
"""

from market_structure import MarketStructure
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
        mtf_results = {}
        for tf in TIMEFRAMES:
            try:
                df = self.data.get_ohlcv(symbol, timeframe=tf)
                df = IndicatorEngine.calculate(df)

                structure = MarketStructure.analyze(df)
                trend_raw = structure["trend"]
                if trend_raw == "bullish":
                    trend_label = "Bullish"
                elif trend_raw == "bearish":
                    trend_label = "Bearish"
                else:
                    trend_label = "Sideways"

                mtf_results[tf] = trend_label
            except Exception:
                mtf_results[tf] = "Neutral"

        mtf_signal = MTFEngine.analyze(mtf_results)
        return (mtf_signal, mtf_results)

    def scan(self):
        results = []
        symbols = self.get_symbols()
        print(f"Scanning {len(symbols)} symbols...\n")

        for symbol in symbols:
            try:
                df = self.data.get_ohlcv(symbol)
                df = IndicatorEngine.calculate(df)

                market_structure = MarketStructure.analyze(df)
                raw_trend = market_structure["trend"]
                trend_map = {"bullish": "Bullish", "bearish": "Bearish", "sideways": "Sideways"}
                trend = trend_map.get(raw_trend, "Sideways")

                strength = TrendEngine.strength(df)

                mtf_signal, mtf_details = self.analyze_mtf(symbol)

                analysis = ScoringEngine.calculate(
                    df,
                    mtf_signal,
                    market_structure=market_structure,
                    strength=strength        # ارسال قدرت روند
                )

                base_score = analysis["base_score"]
                mtf_bonus = analysis["mtf_bonus"]
                score = analysis["score"]
                confidence = analysis["confidence"]
                breakout = analysis["breakout"]
                reasons = analysis["reasons"]
                warnings = analysis["warnings"]

                # ترتیب Reasons به صورت زیر تضمین شده:
                # 1- Market Structure, BOS/CHoCH
                # 2- MTF
                # 3- EMA
                # 4- ADX/DI
                # 5- RSI
                # 6- MACD
                # 7- Volume
                # (همان‌طور که در scoring.py ترتیب داده شده)

                action = ScoringEngine.action(score, breakout)

                # ==============================
                # فیلترهای BUY سخت‌گیرانه
                # ==============================
                if action in ["BUY", "BUY BREAKOUT"]:
                    bos = market_structure.get("bos", [])
                    choch = market_structure.get("choch", [])
                    last_volume_ratio = df["VOLUME_RATIO"].iloc[-1]

                    has_bos_same_direction = False
                    if bos:
                        last_bos = bos[-1]
                        if (trend == "Bullish" and last_bos["type"] == "bullish") or \
                           (trend == "Bearish" and last_bos["type"] == "bearish"):
                            has_bos_same_direction = True

                    has_opposing_choch = False
                    if choch:
                        last_choch = choch[-1]
                        if (trend == "Bullish" and last_choch["type"] == "bearish") or \
                           (trend == "Bearish" and last_choch["type"] == "bullish"):
                            has_opposing_choch = True

                    volume_ok = last_volume_ratio >= 1.0

                    mtf_aligned = False
                    if trend == "Bullish" and ("Bullish" in mtf_signal):
                        mtf_aligned = True
                    elif trend == "Bearish" and ("Bearish" in mtf_signal):
                        mtf_aligned = True

                    if not (has_bos_same_direction and volume_ok and mtf_aligned and not has_opposing_choch):
                        action = "WATCH"
                        if not has_bos_same_direction:
                            warnings.append("Missing BOS confirmation")
                        if not volume_ok:
                            warnings.append("Volume below average")
                        if not mtf_aligned:
                            warnings.append("MTF not aligned with trend")
                        if has_opposing_choch:
                            warnings.append("Opposing CHoCH active")

                # Base Score Filter
                if action in ["BUY", "BUY BREAKOUT"] and base_score < 75:
                    action = "WATCH"
                    warnings.append("Low Base Score")

                # Trend Filters
                if trend == "Sideways":
                    if action in ["BUY", "BUY BREAKOUT"]:
                        action = "WATCH"
                        warnings.append("Sideways Trend (Structure)")
                if trend == "Bearish":
                    action = "NO TRADE"
                    warnings.append("Bearish Trend (Structure)")

                last = df.iloc[-1]

                support = round(df["low"].tail(50).min(), 4)
                resistance = round(df["high"].tail(50).max(), 4)

                atr = float(last["ATR"])
                entry = round(last["close"], 4)
                stop_loss = round(entry - (atr * 1.5), 4)
                take_profit = round(entry + (atr * 3), 4)

                results.append({
                    "Symbol": symbol,
                    "Price": entry,
                    "Trend": trend,
                    "Strength": strength,
                    "MTF_Signal": mtf_signal,
                    "MTF_Details": mtf_details,
                    "Confidence": confidence,
                    "RSI": round(last["RSI"], 2),
                    "Base Score": base_score,
                    "MTF Bonus": mtf_bonus,
                    "Score": score,
                    "Action": action,
                    "Support": support,
                    "Resistance": resistance,
                    "Entry": entry,
                    "StopLoss": stop_loss,
                    "TakeProfit": take_profit,
                    "Volume Breakout": breakout,
                    "Reasons": ", ".join(reasons),
                    "Warnings": ", ".join(warnings)
                })

            except Exception as e:
                print(f"{symbol} : {e}")

        results = sorted(results, key=lambda x: x["Score"], reverse=True)
        return results[:TOP_RESULTS]
