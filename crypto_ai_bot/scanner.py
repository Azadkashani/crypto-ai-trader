"""
Crypto AI Bot v1.2
Market Scanner – Adaptive Sizing, Liquidity Execution, Expected Value, Trade Valid Logic
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
    ENABLE_ADAPTIVE_POSITION_SIZING, ENABLE_LIQUIDITY_EXECUTION, ENABLE_EXPECTED_VALUE,
    MIN_EXECUTION_QUALITY, MIN_EXPECTED_VALUE
)
import config as cfg
from data import MarketData
from indicators import IndicatorEngine
from trend import TrendEngine
from scoring import ScoringEngine
from decision_engine import DecisionEngine
from risk_manager import RiskManager
from mtf_engine import MTFEngine
from timeframe import TIMEFRAMES
from trade_planner import TradePlanner
from execution_analyzer import ExecutionAnalyzer
from expected_value import ExpectedValue

# News & Sentiment
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
        self.planner = TradePlanner(cfg)

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

        # اخبار و تحلیل اولیه
        all_raw_news = []
        analyzed_news = []
        if ENABLE_NEWS_ENGINE:
            all_raw_news = NewsEngine.fetch_news()
            analyzed_news = [NewsAnalyzer.analyze(n) for n in all_raw_news]
            for news in analyzed_news:
                news["assets"] = NewsMapping.get_related_assets(news["title"])

        global_sentiment = MarketSentiment.fetch_global_sentiment() if ENABLE_SENTIMENT_ENGINE else None

        calendar_events = EconomicCalendar.fetch_events() if ENABLE_ECONOMIC_CALENDAR else []
        macro_risk_active, macro_event = RiskEvents.is_high_impact_near(calendar_events)

        for symbol in symbols:
            try:
                # حجم و فیلتر
                try:
                    ticker = self.data.exchange.fetch_ticker(symbol)
                    volume_24h = ticker.get("quoteVolume", 0) or 0
                except:
                    volume_24h = 0
                if volume_24h < MIN_24H_VOLUME:
                    continue

                df = self.data.get_ohlcv(symbol)
                df = IndicatorEngine.calculate(df)

                market_structure = MarketStructure.analyze(df)
                raw_trend = market_structure["trend"]
                trend = raw_trend.capitalize()
                strength = TrendEngine.strength(df)
                mtf_signal, _ = self.analyze_mtf(symbol)
                advanced_data = self.advanced.analyze(df, market_structure, symbol)

                # News & Sentiment
                news_score_val = 0
                sentiment_score_val = 0
                relevant_news = []
                asset_sentiment = {}
                if ENABLE_NEWS_ENGINE:
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

                # Scoring
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

                # Decision اولیه (بدون پارامترهای plan)
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

                initial_action = decision["action"]
                original_side = "sell" if "SELL" in initial_action else "buy"

                entry = float(df.iloc[-1]["close"])
                atr_val = df["ATR"].iloc[-1] if df["ATR"].iloc[-1] > 0 else 0.0001

                # Trade Planner (همیشه اجرا می‌شود، اما فقط برای BUY/SELL اعمال می‌شود)
                plan = self.planner.plan(df, market_structure, advanced_data, initial_action, entry)

                # Adaptive Position Sizing
                if ENABLE_ADAPTIVE_POSITION_SIZING:
                    market_structure_quality = 1.0 if market_structure.get("trend") in ("bullish", "bearish") else 0.5
                    mtf_agreement = 0.0
                    if "Bullish" in mtf_signal and original_side == "buy":
                        mtf_agreement = 1.0
                    elif "Bearish" in mtf_signal and original_side == "sell":
                        mtf_agreement = 1.0
                    elif "Bullish" in mtf_signal or "Bearish" in mtf_signal:
                        mtf_agreement = 0.5
                    avg_vol = df["volume"].tail(20).mean()
                    std_vol = df["volume"].tail(20).std()
                    vol_z = (df["volume"].iloc[-1] - avg_vol) / std_vol if std_vol != 0 else 0

                    risk_pct = RiskManager.adaptive_risk_pct(
                        atr_val, df["ADX"].iloc[-1], market_structure_quality,
                        decision["confidence"], decision["trade_readiness"],
                        mtf_agreement, vol_z, news_score_val, sentiment_score_val,
                        macro_risk_active
                    )
                else:
                    risk_pct = cfg.RISK_PER_TRADE

                # Liquidity Execution
                exec_analysis = {}
                if ENABLE_LIQUIDITY_EXECUTION:
                    exec_analysis = ExecutionAnalyzer.analyze(
                        df, market_structure, advanced_data, initial_action, entry
                    )

                # Expected Value (با استفاده از targets و stop_loss واقعی)
                ev = 0.0
                if ENABLE_EXPECTED_VALUE and plan["targets"]:
                    volatility_state = advanced_data.get("atr_volatility", {}).get("volatility", "Normal") if advanced_data else "Normal"
                    ev = ExpectedValue.calculate(
                        plan["targets"], entry, plan.get("stop_loss", entry - atr_val),
                        decision["confidence"], decision["trade_readiness"],
                        strength, news_score_val, sentiment_score_val,
                        volatility_state, vol_z
                    )

                # تصمیم‌گیری نهایی با در نظر گرفتن اعتبار طرح
                final_action = initial_action
                if initial_action in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"):
                    if not plan["valid"]:
                        final_action = "WATCH"
                        decision["summary"]["Current Status"] = f"Trade rejected: {', '.join(plan['reasons'])}"
                    elif ENABLE_EXPECTED_VALUE and ev <= MIN_EXPECTED_VALUE:
                        final_action = "WATCH"
                        decision["summary"]["Current Status"] += f" EV={ev}R"
                    elif ENABLE_LIQUIDITY_EXECUTION and exec_analysis.get("execution_quality", 100) < MIN_EXECUTION_QUALITY:
                        final_action = "WATCH"
                        decision["summary"]["Current Status"] += f" ExecQual={exec_analysis['execution_quality']}"

                # Trade Valid فقط برای BUY/SELL نهایی
                trade_valid = (final_action in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"))

                # مقادیر نهایی برای ذخیره
                stop_loss = plan["stop_loss"]
                targets = plan["targets"]
                tp1 = targets[0]["price"] if targets else entry + (atr_val * 3)
                rr = plan["rr"]

                # Leverage پویا
                suggested_leverage = RiskManager.suggest_leverage(entry, stop_loss, original_side,
                                                                  volatility=volatility_state if ENABLE_EXPECTED_VALUE else "Normal",
                                                                  confidence=decision["confidence"],
                                                                  execution_quality=exec_analysis.get("execution_quality", 50),
                                                                  ev=ev)
                input_pct = risk_pct * 100

                # Position Risk Reason
                position_risk_reason = ""
                if ENABLE_ADAPTIVE_POSITION_SIZING:
                    parts = []
                    if atr_val > 0.05: parts.append("Very High Volatility")
                    elif atr_val > 0.03: parts.append("High Volatility")
                    elif atr_val < 0.01: parts.append("Low Volatility")
                    if df["ADX"].iloc[-1] >= 40: parts.append("Strong Trend")
                    elif df["ADX"].iloc[-1] < 15: parts.append("Weak Trend")
                    if decision["confidence"] > 80: parts.append("High Confidence")
                    if decision["trade_readiness"] > 80: parts.append("High Readiness")
                    if mtf_agreement == 1.0: parts.append("MTF Aligned")
                    elif mtf_agreement == 0.5: parts.append("Partial MTF")
                    if vol_z > 1.0: parts.append("High Volume")
                    if news_score_val > 5: parts.append("Positive News")
                    elif news_score_val < -5: parts.append("Negative News")
                    if macro_risk_active: parts.append("Macro Risk")
                    position_risk_reason = ", ".join(parts) if parts else "Neutral"
                else:
                    position_risk_reason = "Fixed 1%"

                results.append({
                    "Symbol": symbol,
                    "Price": entry,
                    "Trend": trend,
                    "Strength": strength,
                    "MTF_Signal": mtf_signal,
                    "Confidence": decision["confidence"],
                    "RSI": round(df["RSI"].iloc[-1], 2),
                    "Buy Score": buy_score,
                    "Sell Score": sell_score,
                    "Score": score,
                    "Action": final_action,
                    "Market Signal": trend,
                    "Trade Valid": trade_valid,
                    "Support": round(df["low"].tail(50).min(), 4),
                    "Resistance": round(df["high"].tail(50).max(), 4),
                    "Entry": entry,
                    "StopLoss": stop_loss,
                    "TP1": tp1,
                    "Targets": targets,
                    "RiskReward": round(rr, 2),
                    "Leverage": suggested_leverage,
                    "InputPct": input_pct,
                    "PositionRisk": f"{risk_pct*100:.2f}%",
                    "PositionRiskReason": position_risk_reason,
                    "ExecutionType": exec_analysis.get("execution_type", "N/A"),
                    "ExecutionQuality": exec_analysis.get("execution_quality", 0),
                    "ExpectedValue": f"{ev:+.2f}R",
                    "VolumeUSDT": round(volume_24h, 2),
                    "Volume Breakout": breakout,
                    "Reasons": ", ".join(reasons),
                    "Warnings": ", ".join(warnings),
                    "Weighted Reasons": weighted_reasons,
                    "Weighted Warnings": weighted_warnings,
                    "Summary": decision["summary"],
                    "Entry Quality": decision["entry_quality"],
                    "Trade Readiness": decision["trade_readiness"],
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
