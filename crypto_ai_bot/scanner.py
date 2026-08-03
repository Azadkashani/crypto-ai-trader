"""
Crypto AI Bot v1.2
Market Scanner + Multi Timeframe Engine (Signal-Only + Dynamic Leverage + Input% + Enhanced Fundamental Analysis)
"""

from market_structure import MarketStructure
from config import (
    SYMBOLS, USE_ALL_MARKETS, MAX_SYMBOLS, TOP_RESULTS, MIN_24H_VOLUME,
    ENABLE_LIQUIDITY_SWEEP, ENABLE_FVG, ENABLE_ORDER_BLOCK, ENABLE_PREMIUM_DISCOUNT,
    ENABLE_VOLUME_PROFILE, ENABLE_VWAP, ENABLE_OPEN_INTEREST, ENABLE_FUNDING_RATE,
    ENABLE_ATR_VOLATILITY, ENABLE_EMA_SLOPE, ENABLE_RSI_DIVERGENCE, ENABLE_MACD_DIVERGENCE,
    ENABLE_CANDLESTICK_PATTERNS, ENABLE_SR_STRENGTH, ENABLE_BREAKOUT_QUALITY,
    ENABLE_TRENDLINE_BREAK, ENABLE_FIBONACCI, ENABLE_SESSION_DETECTION,
    ENABLE_MARKET_REGIME, ENABLE_CORRELATION_FILTER,
    ENABLE_NEWS_ENGINE, ENABLE_SENTIMENT_ENGINE, ENABLE_ECONOMIC_CALENDAR,
)
from data import MarketData
from indicators import IndicatorEngine
from trend import TrendEngine
from scoring import ScoringEngine
from decision_engine import DecisionEngine
from risk_manager import RiskManager
from mtf_engine import MTFEngine
from timeframe import TIMEFRAMES

# News & Sentiment imports
from news_engine import NewsEngine
from news_analyzer import NewsAnalyzer
from news_mapping import NewsMapping
from market_sentiment import MarketSentiment
from news_scoring import NewsScoring
from economic_calendar import EconomicCalendar
from risk_events import RiskEvents

# Advanced Analytics
from advanced_analytics import AdvancedAnalytics


class MarketScanner:

    def __init__(self):
        self.data = MarketData()
        self.advanced = AdvancedAnalytics(data_engine=self.data)

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

        # === دریافت اخبار و تحلیل اولیه ===
        all_raw_news = []
        analyzed_news = []
        if ENABLE_NEWS_ENGINE:
            all_raw_news = NewsEngine.fetch_news()
            analyzed_news = [NewsAnalyzer.analyze(n) for n in all_raw_news]
            # افزودن assets به هر خبر با NewsMapping جدید (v1.2)
            for news in analyzed_news:
                news["assets"] = NewsMapping.get_related_assets(news["title"])

        # Global sentiment (یک بار برای همه)
        global_sentiment = MarketSentiment.fetch_global_sentiment() if ENABLE_SENTIMENT_ENGINE else None

        calendar_events = EconomicCalendar.fetch_events() if ENABLE_ECONOMIC_CALENDAR else []
        macro_risk_active, macro_event = RiskEvents.is_high_impact_near(calendar_events)

        for symbol in symbols:
            try:
                # === دریافت حجم ۲۴ ساعته و فیلتر حجم ===
                try:
                    ticker = self.data.exchange.fetch_ticker(symbol)
                    volume_24h = ticker.get("quoteVolume", 0) or 0
                except Exception:
                    volume_24h = 0

                if volume_24h < MIN_24H_VOLUME:
                    continue   # رد کردن نمادهای کم‌حجم

                df = self.data.get_ohlcv(symbol)
                df = IndicatorEngine.calculate(df)

                market_structure = MarketStructure.analyze(df)
                raw_trend = market_structure["trend"]
                trend = raw_trend.capitalize()

                strength = TrendEngine.strength(df)

                mtf_signal, mtf_details = self.analyze_mtf(symbol)

                # === Advanced Analytics واقعی ===
                advanced_data = self.advanced.analyze(df, market_structure, symbol)

                # === News Score (v1.2: per-symbol with multi-level weighting) ===
                news_score_val = 0
                sentiment_score_val = 0
                relevant_news = []
                asset_sentiment = {}
                if ENABLE_NEWS_ENGINE:
                    # Asset sentiment مخصوص این نماد
                    asset_sentiment = MarketSentiment.fetch_asset_sentiment(self.data.exchange, symbol) if ENABLE_SENTIMENT_ENGINE else {}
                    base_coin = symbol.split("/")[0]
                    related_news = []
                    for news in analyzed_news:
                        assets = news.get("assets", [])
                        for a in assets:
                            if a["symbol"] == base_coin or a["symbol"] == "MARKET":
                                related_news.append(news)
                                break
                    scores = NewsScoring.calculate(related_news, global_sentiment, asset_sentiment, symbol)
                    news_score_val = scores["news_score"]
                    sentiment_score_val = scores["sentiment_score"]
                    relevant_news = related_news

                # === Scoring (همان نسخه متقارن v1.1) ===
                analysis = ScoringEngine.calculate(
                    df, mtf_signal,
                    market_structure=market_structure,
                    strength=strength,
                    advanced_data=advanced_data,
                    news_score=news_score_val,
                    sentiment_score=sentiment_score_val
                )

                buy_score = analysis["buy_score"]
                sell_score = analysis["sell_score"]
                score = analysis["score"]
                breakout = analysis["breakout"]
                reasons = analysis["reasons"]
                warnings = analysis["warnings"]
                weighted_reasons = analysis.get("weighted_reasons", [])
                weighted_warnings = analysis.get("weighted_warnings", [])

                # === Decision (مقایسه buy_score / sell_score) ===
                decision = DecisionEngine.evaluate(
                    df, market_structure, mtf_signal, strength,
                    advanced_data,
                    buy_score=buy_score,
                    sell_score=sell_score,
                    breakout=breakout,
                    reasons=reasons,
                    warnings=warnings,
                    risk_event=macro_risk_active,
                    news_score=news_score_val,
                    sentiment_score=sentiment_score_val
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
                entry = float(last["close"])

                # ----- محاسبه SL و TP -----
                if "SELL" in action:
                    stop_loss = entry + (atr_val * 1.5)
                    side = "sell"
                else:
                    stop_loss = entry - (atr_val * 1.5)
                    side = "buy"

                if side == "sell":
                    tp1 = entry - (atr_val * 3)
                else:
                    tp1 = entry + (atr_val * 3)

                # اهرم پویا و Input%
                suggested_leverage = RiskManager.suggest_leverage(entry, stop_loss, side)
                sl_pct = abs((stop_loss - entry) / entry) if entry != 0 else 0
                if sl_pct < 0.01:
                    input_pct = 100.0
                else:
                    input_pct = round((1.0 / (sl_pct * 100)) * 100, 2)

                results.append({
                    "Symbol": symbol,
                    "Price": entry,
                    "Trend": trend,
                    "Strength": strength,
                    "MTF_Signal": mtf_signal,
                    "MTF_Details": mtf_details,
                    "Confidence": confidence,
                    "RSI": round(last["RSI"], 2),
                    "Buy Score": buy_score,
                    "Sell Score": sell_score,
                    "Score": score,
                    "Action": action,
                    "Support": support,
                    "Resistance": resistance,
                    "Entry": entry,
                    "StopLoss": stop_loss,
                    "TP1": tp1,
                    "Leverage": suggested_leverage,
                    "InputPct": input_pct,
                    "VolumeUSDT": round(volume_24h, 2),
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
                    "Global Sentiment": global_sentiment,
                    "Asset Sentiment": asset_sentiment,
                    "Macro Risk": macro_risk_active,
                    "Macro Event": macro_event["title"] if macro_risk_active else None,
                    "Relevant News": relevant_news,
                    "advanced": advanced_data
                })

            except Exception as e:
                print(f"{symbol} : {e}")

        results = sorted(results, key=lambda x: x["Trade Readiness"], reverse=True)
        return results[:TOP_RESULTS]
