"""
Crypto AI Bot v5.7
Market Scanner + Multi Timeframe Engine (Decision Engine)
"""

from market_structure import MarketStructure
from config import (
    SYMBOLS,
    USE_ALL_MARKETS,
    MAX_SYMBOLS,
    TOP_RESULTS,
    ENABLE_LIQUIDITY_SWEEP,
    ENABLE_FVG,
    ENABLE_ORDER_BLOCK,
    ENABLE_PREMIUM_DISCOUNT,
    ENABLE_VOLUME_PROFILE,
    ENABLE_VWAP,
    ENABLE_OPEN_INTEREST,
    ENABLE_FUNDING_RATE,
    ENABLE_ATR_VOLATILITY,
    ENABLE_EMA_SLOPE,
    ENABLE_RSI_DIVERGENCE,
    ENABLE_MACD_DIVERGENCE,
    ENABLE_CANDLESTICK_PATTERNS,
    ENABLE_SR_STRENGTH,
    ENABLE_BREAKOUT_QUALITY,
    ENABLE_TRENDLINE_BREAK,
    ENABLE_FIBONACCI,
    ENABLE_SESSION_DETECTION,
    ENABLE_MARKET_REGIME,
    ENABLE_CORRELATION_FILTER,
)

from data import MarketData
from indicators import IndicatorEngine
from trend import TrendEngine
from scoring import ScoringEngine

from mtf_engine import MTFEngine
from timeframe import TIMEFRAMES
from decision_engine import DecisionEngine


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
                trend = raw_trend.capitalize()

                strength = TrendEngine.strength(df)

                mtf_signal, mtf_details = self.analyze_mtf(symbol)

                advanced_data = None
                if any([
                    ENABLE_LIQUIDITY_SWEEP, ENABLE_FVG, ENABLE_ORDER_BLOCK,
                    ENABLE_PREMIUM_DISCOUNT, ENABLE_VOLUME_PROFILE, ENABLE_VWAP,
                    ENABLE_OPEN_INTEREST, ENABLE_FUNDING_RATE, ENABLE_ATR_VOLATILITY,
                    ENABLE_EMA_SLOPE, ENABLE_RSI_DIVERGENCE, ENABLE_MACD_DIVERGENCE,
                    ENABLE_CANDLESTICK_PATTERNS, ENABLE_SR_STRENGTH, ENABLE_BREAKOUT_QUALITY,
                    ENABLE_TRENDLINE_BREAK, ENABLE_FIBONACCI, ENABLE_SESSION_DETECTION,
                    ENABLE_MARKET_REGIME, ENABLE_CORRELATION_FILTER
                ]):
                    from advanced_analytics import AdvancedAnalytics
                    aa = AdvancedAnalytics(data_engine=self.data)
                    advanced_data = aa.analyze(df, market_structure=market_structure, symbol=symbol)

                analysis = ScoringEngine.calculate(
                    df,
                    mtf_signal,
                    market_structure=market_structure,
                    strength=strength,
                    advanced_data=advanced_data
                )

                base_score = analysis["base_score"]
                mtf_bonus = analysis["mtf_bonus"]
                score = analysis["score"]
                breakout = analysis["breakout"]
                reasons = analysis["reasons"]
                warnings = analysis["warnings"]
                weighted_reasons = analysis.get("weighted_reasons", [])
                weighted_warnings = analysis.get("weighted_warnings", [])

                # ==============================
                # Decision Engine
                # ==============================
                decision = DecisionEngine.evaluate(
                    df, market_structure, mtf_signal, strength,
                    advanced_data, score, breakout, reasons, warnings
                )

                action = decision["action"]
                confidence = decision["confidence"]
                trade_readiness = decision["trade_readiness"]
                entry_quality = decision["entry_quality"]
                summary = decision["summary"]

                last = df.iloc[-1]
                atr_val = last["ATR"] if last["ATR"] > 0 else 0.0001
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
                    "Warnings": ", ".join(warnings),
                    "Weighted Reasons": weighted_reasons,
                    "Weighted Warnings": weighted_warnings,
                    "Summary": summary,
                    "Entry Quality": entry_quality,
                    "Trade Readiness": trade_readiness,
                    "advanced": advanced_data
                })

            except Exception as e:
                print(f"{symbol} : {e}")

        results = sorted(results, key=lambda x: x["Trade Readiness"], reverse=True)
        return results[:TOP_RESULTS]
