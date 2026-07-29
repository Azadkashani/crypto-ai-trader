"""
Crypto AI Bot v5.7
Market Scanner + Multi Timeframe Engine (Balanced & Professional)
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
                trend_label = "Bullish" if trend_raw == "bullish" else \
                              "Bearish" if trend_raw == "bearish" else "Sideways"
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

                # دلایل ضعف روند
                weak_reasons = []
                if strength in ("Weak", "Medium"):
                    last_tmp = df.iloc[-1]
                    if last_tmp["ADX"] < 20:
                        weak_reasons.append("Low ADX")
                    if abs(last_tmp["EMA20"] - last_tmp["EMA50"]) / last_tmp["EMA50"] < 0.01:
                        weak_reasons.append("Small EMA spread")
                    if last_tmp["volume"] <= last_tmp["AVG_VOLUME"]:
                        weak_reasons.append("No volume confirmation")
                if weak_reasons:
                    weak_msg = "Weak: " + ", ".join(weak_reasons)
                else:
                    weak_msg = None

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

                if weak_msg:
                    warnings.append(weak_msg)

                # تعیین Action اولیه
                action = ScoringEngine.action(score, breakout)

                last = df.iloc[-1]
                atr_val = last["ATR"] if last["ATR"] > 0 else 0.0001
                resistance_20 = df["high"].tail(20).max()
                support_20 = df["low"].tail(20).min()
                distance_pct = (resistance_20 - last["close"]) / last["close"] * 100 if last["close"] > 0 else 100

                # فیلترهای هوشمند Action
                if action in ["BUY", "BUY BREAKOUT"]:
                    bos = market_structure.get("bos", [])
                    last_bos = bos[-1] if bos else None
                    has_bos = last_bos and ((trend == "Bullish" and last_bos["type"] == "bullish") or
                                            (trend == "Bearish" and last_bos["type"] == "bearish"))
                    last_event = market_structure.get("last_event")
                    opposing_choch = (last_event and last_event["event"] == "choch" and
                                      ((trend == "Bullish" and last_event["type"] == "bearish") or
                                       (trend == "Bearish" and last_event["type"] == "bullish")))
                    vol_ok = last["volume"] > last["AVG_VOLUME"]
                    mtf_ok = (trend == "Bullish" and "Bullish" in mtf_signal) or \
                             (trend == "Bearish" and "Bearish" in mtf_signal)
                    adx_ok = last["ADX"] >= 20
                    location_ok = distance_pct >= 2.0
                    rr_ok = (last["close"] - support_20) / atr_val >= 1.5

                    if not (has_bos and vol_ok and mtf_ok and adx_ok and location_ok and rr_ok and not opposing_choch):
                        action = "WATCH"
                        if not has_bos:
                            warnings.append("No BOS")
                        if not vol_ok:
                            warnings.append("Low Volume")
                        if not mtf_ok:
                            warnings.append("MTF Not Aligned")
                        if not adx_ok:
                            warnings.append("ADX < 20")
                        if not location_ok:
                            warnings.append("Near Resistance (<2%)")
                        if not rr_ok:
                            warnings.append("Low R/R")
                        if opposing_choch:
                            warnings.append("Opposing CHoCH active")

                # WATCH فقط با BOS و امتیاز حداقل ۴۵
                if action == "WATCH":
                    bos = market_structure.get("bos", [])
                    if not bos or score < 45:
                        action = "NO TRADE"

                # فیلتر روند
                if trend == "Bearish":
                    action = "NO TRADE"
                    warnings.append("Bearish Trend")
                elif trend == "Sideways" and action != "NO TRADE":
                    action = "WATCH"
                    warnings.append("Sideways Trend")

                # ساخت خروجی
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
