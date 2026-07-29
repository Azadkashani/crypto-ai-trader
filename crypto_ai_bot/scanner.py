"""
Crypto AI Bot v5.7
Market Scanner + Multi Timeframe Engine (Final)
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
                    strength=strength
                )

                base_score = analysis["base_score"]
                mtf_bonus = analysis["mtf_bonus"]
                score = analysis["score"]
                confidence = analysis["confidence"]
                breakout = analysis["breakout"]
                reasons = analysis["reasons"]
                warnings = analysis["warnings"]

                # ==============================
                # تعیین Action اولیه
                # ==============================
                action = ScoringEngine.action(score, breakout)

                # ==============================
                # فیلترهای سختگیرانه BUY/WATCH
                # ==============================
                last = df.iloc[-1]
                atr_val = last["ATR"] if last["ATR"] > 0 else 0.0001
                resistance_20 = df["high"].tail(20).max()
                support_20 = df["low"].tail(20).min()
                distance_to_res = (resistance_20 - last["close"]) / atr_val

                # شرایط BUY
                if action in ["BUY", "BUY BREAKOUT"]:
                    bos = market_structure.get("bos", [])
                    last_bos = bos[-1] if bos else None
                    has_bos = last_bos is not None and \
                              ((trend == "Bullish" and last_bos["type"] == "bullish") or \
                               (trend == "Bearish" and last_bos["type"] == "bearish"))

                    choch = market_structure.get("choch", [])
                    last_choch = choch[-1] if choch else None
                    opposing_choch = last_choch and \
                        ((trend == "Bullish" and last_choch["type"] == "bearish") or \
                         (trend == "Bearish" and last_choch["type"] == "bullish"))

                    vol_ok = last["volume"] > last["AVG_VOLUME"]
                    mtf_ok = (trend == "Bullish" and "Bullish" in mtf_signal) or \
                             (trend == "Bearish" and "Bearish" in mtf_signal)
                    adx_ok = last["ADX"] >= 20
                    location_ok = distance_to_res >= 2.0
                    rr_ok = (last["close"] - support_20) / atr_val >= 1.5  # فاصله تا حمایت حداقل 1.5 ATR

                    if not (has_bos and vol_ok and mtf_ok and adx_ok and location_ok and rr_ok and not opposing_choch):
                        action = "WATCH"
                        if not has_bos: warnings.append("No BOS")
                        if not vol_ok: warnings.append("Low Volume")
                        if not mtf_ok: warnings.append("MTF Not Aligned")
                        if not adx_ok: warnings.append("ADX < 20")
                        if not location_ok: warnings.append("Near Resistance")
                        if not rr_ok: warnings.append("Low R/R")
                        if opposing_choch: warnings.append("Opposing CHoCH")

                # تبدیل WATCH به NO TRADE اگر امتیاز پایین باشد یا BOS نباشد
                if action == "WATCH":
                    bos = market_structure.get("bos", [])
                    if not bos or score < 45:
                        action = "NO TRADE"

                # فیلتر نهایی روند
                if trend == "Bearish":
                    action = "NO TRADE"
                    warnings.append("Bearish Trend")
                elif trend == "Sideways" and action != "NO TRADE":
                    action = "WATCH"
                    warnings.append("Sideways Trend")

                # ==============================
                # ساخت نتایج
                # ==============================
                support = round(df["low"].tail(50).min(), 4)
                resistance = round(df["high"].tail(50).max(), 4)

                entry = round(last["close"], 4)
                stop_loss = round(entry - (atr_val * 1.5), 4)
                take_profit = round(entry + (atr_val * 3), 4)

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
