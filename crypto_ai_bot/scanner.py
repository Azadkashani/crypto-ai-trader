"""
Crypto AI Bot v1.2
Market Scanner – Strict RR, unified trade_valid, separated targets
"""

import traceback
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
    MIN_EXECUTION_QUALITY, MIN_EXPECTED_VALUE,
    ACCOUNT_BALANCE, MIN_RISK_REWARD
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
                if trend == "Bullish":
                    plan_action = "BUY"
                    original_side = "buy"
                elif trend == "Bearish":
                    plan_action = "SELL"
                    original_side = "sell"
                else:
                    plan_action = "WATCH"
                    original_side = "buy"

                entry = float(df.iloc[-1]["close"])
                atr_val = df["ATR"].iloc[-1] if df["ATR"].iloc[-1] > 0 else 0.0001

                plan = self.planner.plan(df, market_structure, advanced_data, plan_action, entry)

                # Strict RR – no adaptive bypass
                trade_valid = plan["valid"]
                final_action = initial_action
                if initial_action in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"):
                    if not plan["valid"]:
                        final_action = "WATCH"
                        trade_valid = False
                        decision["summary"]["Current Status"] = f"Trade rejected: {', '.join(plan['reasons'])}"
                    else:
                        trade_valid = True  # plan valid, keep action

                # After all checks, ensure trade_valid matches final_action
                trade_valid = (final_action in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"))

                # Execution analysis (safe)
                exec_analysis = {
                    "execution_type": "Unknown",
                    "execution_quality": 0,
                    "liquidity_risk": 0
                }
                if ENABLE_LIQUIDITY_EXECUTION:
                    try:
                        exec_analysis = ExecutionAnalyzer.analyze(
                            df, market_structure, advanced_data, plan_action, entry
                        )
                    except Exception:
                        traceback.print_exc()

                liq_risk_val = exec_analysis["liquidity_risk"]
                if liq_risk_val > 50:
                    liq_label = "High"
                elif liq_risk_val > 20:
                    liq_label = "Medium"
                else:
                    liq_label = "Low"

                # Position Sizing
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

                    btc_corr = None
                    corr_data = advanced_data.get("correlation")
                    if corr_data and "btc_correlation" in corr_data:
                        btc_corr = corr_data["btc_correlation"]

                    risk_pct = RiskManager.adaptive_risk_pct(
                        atr_val, df["ADX"].iloc[-1], market_structure_quality,
                        decision["confidence"], decision["trade_readiness"],
                        mtf_agreement, vol_z, news_score_val, sentiment_score_val,
                        macro_risk_active,
                        execution_quality=exec_analysis["execution_quality"],
                        ev=plan.get("best_ev", 0), btc_corr=btc_corr, warnings=warnings
                    )
                else:
                    risk_pct = cfg.RISK_PER_TRADE

                risk_amount = ACCOUNT_BALANCE * risk_pct
                sl_distance = abs(entry - plan["stop_loss"])
                position_size = risk_amount / sl_distance if sl_distance > 0 else 0.0

                risk_level = "High" if risk_pct >= cfg.MAX_POSITION_RISK * 0.8 else \
                             "Medium" if risk_pct >= cfg.MIN_POSITION_RISK * 2 else "Low"

                # Expected Value (only when valid)
                ev = None
                if ENABLE_EXPECTED_VALUE and trade_valid and plan["targets"]:
                    volatility_state = advanced_data.get("atr_volatility", {}).get("volatility", "Normal") if advanced_data else "Normal"
                    ev = ExpectedValue.calculate(
                        plan["targets"], entry, plan.get("stop_loss", entry - atr_val),
                        decision["confidence"], decision["trade_readiness"],
                        strength, news_score_val, sentiment_score_val,
                        volatility_state, vol_z
                    )

                suggested_leverage = RiskManager.suggest_leverage(
                    entry, plan["stop_loss"], original_side,
                    volatility=volatility_state if ENABLE_EXPECTED_VALUE else "Normal",
                    confidence=decision["confidence"],
                    execution_quality=exec_analysis["execution_quality"],
                    ev=plan.get("best_ev", 0)
                )
                input_pct = risk_pct * 100

                exec_q = exec_analysis["execution_quality"]
                ev_norm = max(0, min(100, (plan.get("best_ev", 0) + 2) * 25))
                risk_score = 100 - (risk_pct / cfg.MAX_POSITION_RISK * 100) if cfg.MAX_POSITION_RISK > 0 else 50
                trade_quality = int(0.3 * decision["confidence"] + 0.2 * exec_q + 0.2 * ev_norm +
                                   0.15 * (100 - min(liq_risk_val, 100)) + 0.15 * risk_score)

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

                watch_info = {}
                if final_action in ("WATCH",):
                    if trend == "Bullish":
                        res_levels = advanced_data.get("sr_strength", {}).get("resistance_level")
                        if not res_levels:
                            res_levels = df["high"].tail(50).max()
                        watch_info["Trigger Price"] = res_levels
                        watch_info["Confirmation"] = "Volume breakout + MTF alignment"
                        watch_info["Invalidation"] = f"Below {plan['stop_loss']:.4f}"
                        watch_info["Direction"] = "Bullish"
                    else:
                        sup_levels = advanced_data.get("sr_strength", {}).get("support_level")
                        if not sup_levels:
                            sup_levels = df["low"].tail(50).min()
                        watch_info["Trigger Price"] = sup_levels
                        watch_info["Confirmation"] = "Volume spike + MTF alignment"
                        watch_info["Invalidation"] = f"Above {plan['stop_loss']:.4f}"
                        watch_info["Direction"] = "Bearish"

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
                    "StopLoss": plan["stop_loss"],
                    "TP1": plan["targets"][0]["price"] if plan["targets"] else entry + (atr_val * 3),
                    "Targets": plan["targets"],
                    "InvalidTargets": plan.get("invalid_targets", []),
                    "RiskReward": round(plan.get("rr", 0), 2),
                    "Leverage": suggested_leverage,
                    "InputPct": input_pct,
                    "PositionRisk": f"{risk_pct*100:.2f}%",
                    "PositionRiskReason": position_risk_reason,
                    "PositionSize": round(position_size, 6) if position_size > 0 else 0,
                    "RiskAmount": round(risk_amount, 2),
                    "RiskLevel": risk_level,
                    "ExecutionType": exec_analysis["execution_type"],
                    "ExecutionQuality": exec_analysis["execution_quality"],
                    "LiquidityRisk": liq_label,
                    "ExpectedValue": f"{ev:+.2f}R" if ev is not None else "N/A",
                    "TradeQualityScore": trade_quality,
                    "WatchInfo": watch_info,
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
                traceback.print_exc()

        results = sorted(results, key=lambda x: x["TradeQualityScore"] if x["TradeQualityScore"] > 0 else x["Trade Readiness"], reverse=True)
        return results[:TOP_RESULTS]
