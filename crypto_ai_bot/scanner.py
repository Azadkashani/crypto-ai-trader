"""
Crypto AI Bot v5.7
Market Scanner + Multi Timeframe Engine (Decision Engine + News/Sentiment + SELL)
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
    ENABLE_ECONOMIC_CALENDAR,
)

from data import MarketData
from indicators import IndicatorEngine
from trend import TrendEngine
from scoring import ScoringEngine

from mtf_engine import MTFEngine
from timeframe import TIMEFRAMES
from decision_engine import DecisionEngine

# News & Sentiment imports
from news_engine import NewsEngine
from news_analyzer import NewsAnalyzer
from news_mapping import NewsMapping
from market_sentiment import MarketSentiment
from economic_calendar import EconomicCalendar
from risk_events import RiskEvents
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

        # دریافت اخبار و احساسات یک بار برای همه نمادها (اختیاری)
        all_raw_news = []
        if ENABLE_NEWS_ENGINE:
            all_raw_news = NewsEngine.fetch_news()
        sentiment_data = None
        if ENABLE_SENTIMENT_ENGINE:
            sentiment_data = MarketSentiment.fetch_sentiment(self.data.exchange)
        calendar_events = EconomicCalendar.fetch_events() if ENABLE_ECONOMIC_CALENDAR else []

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

                # ==============================
                # News & Sentiment Scoring
                # ==============================
                news_score_val = 0
                sentiment_score_val = 0
                risk_event = False
                if ENABLE_NEWS_ENGINE or ENABLE_SENTIMENT_ENGINE:
                    analyzed_news = [NewsAnalyzer.analyze(n) for n in all_raw_news]
                    related_news = []
                    for news in analyzed_news:
                        syms = NewsMapping.get_related_symbols(news["title"])
                        if "MARKET" in syms or symbol.split("/")[0] in syms:
                            related_news.append(news)
                    scores = NewsScoring.calculate(related_news, sentiment_data)
                    news_score_val = scores["news_score"]
                    sentiment_score_val = scores["sentiment_score"]
                    risk_event = RiskEvents.is_high_impact_near(related_news, calendar_events)

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

                # ==============================
                # Decision Engine
                # ==============================
                decision = DecisionEngine.evaluate(
                    df, market_structure, mtf_signal, strength,
                    advanced_data, score, breakout, reasons, warnings,
                    risk_event=risk_event
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

                # محاسبه SL/TP بر اساس جهت معامله
                if action in ("SELL", "STRONG SELL"):
                    stop_loss = round(entry + (atr_val * 1.5), 4)   # بالای ورود
                    take_profit = round(entry - (atr_val * 3), 4)   # پایین‌تر
                else:  # LONG (BUY, STRONG BUY)
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
                    "News Score": news_score_val,
                    "Sentiment Score": sentiment_score_val,
                    "advanced": advanced_data
                })

            except Exception as e:
                print(f"{symbol} : {e}")

        results = sorted(results, key=lambda x: x["Trade Readiness"], reverse=True)
        return results[:TOP_RESULTS]
