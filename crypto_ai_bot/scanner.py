"""
Crypto AI Bot v1.1
Market Scanner + Multi Timeframe Engine (Signal-Only + Dynamic Leverage + Input%)
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
    ENABLE_NEWS_ENGINE,
    ENABLE_SENTIMENT_ENGINE,
)

from data import MarketData
from indicators import IndicatorEngine
from trend import TrendEngine
from scoring import ScoringEngine
from decision_engine import DecisionEngine
from risk_manager import RiskManager

from mtf_engine import MTFEngine
from timeframe import TIMEFRAMES

# News & Sentiment
from news_engine import NewsEngine
from news_analyzer import NewsAnalyzer
from news_mapping import NewsMapping
from market_sentiment import MarketSentiment
from news_scoring import NewsScoring


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

        all_raw_news = []
        if ENABLE_NEWS_ENGINE:
            all_raw_news = NewsEngine.fetch_news()
            # تحلیل اخبار یکبار برای همه
            analyzed_news = [NewsAnalyzer.analyze(n) for n in all_raw_news]
            # افزودن currencies به هر خبر
            for news in analyzed_news:
                news["currencies"] = NewsMapping.get_related_symbols(news["title"])
        else:
            analyzed_news = []

        sentiment_data = None
        if ENABLE_SENTIMENT_ENGINE:
            sentiment_data = MarketSentiment.fetch_sentiment(self.data.exchange)

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

                news_score_val = 0
                sentiment_score_val = 0
                macro_news = {"bias": "Neutral", "impact": 0}
                if ENABLE_NEWS_ENGINE:
                    # فیلتر اخبار مرتبط
                    related_news = [n for n in analyzed_news if NewsMapping.get_related_symbols(n["title"])]
                    scores = NewsScoring.calculate(related_news, sentiment_data, symbol)
                    news_score_val = scores["news_score"]
                    sentiment_score_val = scores["sentiment_score"]
                    # Macro News summary
                    if news_score_val > 0:
                        macro_news = {"bias": "Bullish", "impact": news_score_val}
                    elif news_score_val < 0:
                        macro_news = {"bias": "Bearish", "impact": news_score_val}
                    else:
                        macro_news = {"bias": "Neutral", "impact": 0}

                analysis = ScoringEngine.calculate(
                    df,
                    mtf_signal,
                    market_structure=market_structure,
                    strength=strength,
                    advanced_data=advanced_data,
                    news_score=news_score_val,
                    sentiment_score=sentiment_score_val
                )

                base_score = analysis["base_score"]
                mtf_bonus = analysis["mtf_bonus"]
                score = analysis["score"]
                breakout = analysis["breakout"]
                reasons = analysis["reasons"]
                warnings = analysis["warnings"]
                weighted_reasons = analysis.get("weighted_reasons", [])
                weighted_warnings = analysis.get("weighted_warnings", [])

                decision = DecisionEngine.evaluate(
                    df, market_structure, mtf_signal, strength,
                    advanced_data, score, breakout, reasons, warnings,
                    risk_event=False
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

                if "SELL" in action:
                    stop_loss = round(entry + (atr_val * 1.5), 4)
                    take_profit = round(entry - (atr_val * 3), 4)
                    side = "sell"
                else:
                    stop_loss = round(entry - (atr_val * 1.5), 4)
                    take_profit = round(entry + (atr_val * 3), 4)
                    side = "buy"

                suggested_leverage = RiskManager.suggest_leverage(entry, stop_loss, side)

                sl_pct = abs((stop_loss - entry) / entry) if entry != 0 else 0
                input_pct = round((1.0 / (sl_pct * 100)) * 100, 2) if sl_pct > 0 else 100.0

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
                    "Leverage": suggested_leverage,
                    "InputPct": input_pct,
                    "Volume Breakout": breakout,
                    "Reasons": ", ".join(reasons),
                    "Warnings": ", ".join(warnings),
                    "Weighted Reasons": weighted_reasons,
                    "Weighted Warnings": weighted_warnings,
                    "Summary": summary,
                    "Entry Quality": entry_quality,
                    "Trade Readiness": trade_readiness,
                    "News Score": news_score_val,
                    "Sentiment Score": sentiment_score_val,
                    "Macro News": macro_news,
                    "advanced": advanced_data
                })

            except Exception as e:
                print(f"{symbol} : {e}")

        results = sorted(results, key=lambda x: x["Trade Readiness"], reverse=True)
        return results[:TOP_RESULTS]
