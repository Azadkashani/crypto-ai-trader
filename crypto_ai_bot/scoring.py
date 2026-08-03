"""
Crypto AI Bot v1.1
Advanced Scoring Engine – Fully Symmetric (independent buy_score & sell_score)
"""

from config import BUY_SCORE, WATCH_SCORE
from weights import REASON_WEIGHTS, WARNING_WEIGHTS


class ScoringEngine:

    @staticmethod
    def calculate(df, mtf_signal="Neutral", market_structure=None, strength="Medium",
                  advanced_data=None, news_score=0, sentiment_score=0):
        last = df.iloc[-1]

        buy_score = 0.0
        sell_score = 0.0
        reasons = []
        warnings = []

        struct_trend = "sideways"
        bos = []
        choch = []
        last_event = None
        if market_structure:
            struct_trend = market_structure.get("trend", "sideways")
            bos = market_structure.get("bos", [])
            choch = market_structure.get("choch", [])
            last_event = market_structure.get("last_event")

        last_bos = bos[-1] if bos else None
        opposing_choch = False
        if last_event and last_event["event"] == "choch":
            if (struct_trend == "bullish" and last_event["type"] == "bearish") or \
               (struct_trend == "bearish" and last_event["type"] == "bullish"):
                opposing_choch = True

        # ========== 1. Market Structure ==========
        if struct_trend == "bullish":
            buy_score += 7
            reasons.append("Market Structure Bullish")
        elif struct_trend == "bearish":
            sell_score += 7
            warnings.append("Market Structure Bearish")

        # ========== 2. BOS ==========
        if last_bos:
            if last_bos["type"] == "bullish":
                buy_score += 12
                reasons.append("BOS Bullish Break")
            else:
                sell_score += 12
                warnings.append("BOS Bearish Break")

        # ========== 3. Multi Timeframe ==========
        mtf_bonus = 0
        if mtf_signal == "Strong Bullish":
            buy_score += 15
            reasons.append("MTF Strong Bullish")
        elif mtf_signal == "Bullish":
            buy_score += 10
            reasons.append("MTF Bullish")
        elif mtf_signal == "Bearish":
            sell_score += 10
            warnings.append("MTF Bearish")
        elif mtf_signal == "Strong Bearish":
            sell_score += 15
            warnings.append("MTF Strong Bearish")

        # ========== 4. EMA ==========
        if last["EMA20"] > last["EMA50"]:
            buy_score += 8
            reasons.append("EMA20 > EMA50")
        else:
            sell_score += 8
            reasons.append("EMA20 < EMA50")

        if last["EMA50"] > last["EMA200"]:
            buy_score += 8
            reasons.append("EMA50 > EMA200")
        else:
            sell_score += 8
            reasons.append("EMA50 < EMA200")

        # ========== 5. ADX & DI ==========
        if last["ADX"] >= 25:
            buy_score += 4
            sell_score += 4
            reasons.append("Strong ADX")

        if last["+DI"] > last["-DI"]:
            buy_score += 5
            reasons.append("+DI > -DI")
        else:
            sell_score += 5
            warnings.append("-DI > +DI")

        # ========== 6. RSI ==========
        rsi = last["RSI"]
        if 45 <= rsi <= 65:
            buy_score += 8
            reasons.append("Healthy RSI (Buy zone)")
        elif 65 < rsi <= 75 and last["ADX"] >= 25:
            buy_score += 6
            reasons.append("Strong Momentum RSI (Buy)")

        if 35 <= rsi <= 55:
            sell_score += 8
            reasons.append("Healthy RSI (Sell zone)")
        elif 25 < rsi <= 35 and last["ADX"] >= 25:
            sell_score += 6
            reasons.append("Strong Momentum RSI (Sell)")

        # ========== 7. MACD ==========
        if last["MACD"] > last["MACD_SIGNAL"]:
            buy_score += 8
            reasons.append("Bullish MACD")
        else:
            sell_score += 8
            warnings.append("Bearish MACD")

        # ========== 8. Volume ==========
        avg_vol = df["volume"].tail(20).mean()
        std_vol = df["volume"].tail(20).std()
        if std_vol > 0:
            vol_z = (last["volume"] - avg_vol) / std_vol
        else:
            vol_z = 0
        if vol_z > 0.5:
            buy_score += 8
            sell_score += 8
            reasons.append("High Volume")
        elif vol_z < -0.5:
            buy_score -= 5
            sell_score -= 5
            warnings.append("Low Volume")

        # ========== 9. Volume Breakout ==========
        resistance_20 = df["high"].tail(20).max()
        breakout = last["close"] > resistance_20 and last["volume"] > 1.2 * avg_vol
        if breakout:
            buy_score += 8
            reasons.append("Volume Breakout")
        # برای فروش، breakdown می‌توانست اضافه شود اما فعلاً متقارن ساده
        support_20 = df["low"].tail(20).min()
        breakdown = last["close"] < support_20 and last["volume"] > 1.2 * avg_vol
        if breakdown:
            sell_score += 8
            warnings.append("Volume Breakdown")

        # ========== 10. Resistance Proximity ==========
        distance_pct = (resistance_20 - last["close"]) / last["close"] * 100 if last["close"] > 0 else 100
        if not breakout and distance_pct < 2.0:
            buy_score -= 5
            sell_score += 5
            warnings.append(f"Price Near Resistance ({distance_pct:.1f}%)")

        # ========== 11. Opposing CHoCH ==========
        if opposing_choch:
            buy_score -= 8
            sell_score -= 8
            warnings.append("Opposing CHoCH (active)")

        # ========== 12. Advanced Analytics ==========
        if advanced_data:
            # -- Liquidity Sweep
            ls = advanced_data.get("liquidity_sweep")
            if ls:
                if ls.get("buy_side_sweep"):
                    buy_score += 5
                    reasons.append("Buy Side Liquidity Sweep")
                if ls.get("sell_side_sweep"):
                    sell_score += 5
                    warnings.append("Sell Side Liquidity Sweep")

            # -- FVG
            fvg = advanced_data.get("fvg")
            if fvg:
                if fvg.get("bullish_fvg"):
                    buy_score += 5
                    reasons.append("Unfilled Bullish FVG")
                if fvg.get("bearish_fvg"):
                    sell_score += 5
                    warnings.append("Unfilled Bearish FVG")

            # -- Order Block
            ob = advanced_data.get("order_block")
            if ob and ob.get("valid"):
                if ob.get("bullish_ob"):
                    buy_score += 6
                    reasons.append("Bullish Order Block")
                elif ob.get("bearish_ob"):
                    sell_score += 6
                    warnings.append("Bearish Order Block")

            # -- Premium/Discount
            pd_zone = advanced_data.get("premium_discount")
            if pd_zone:
                if pd_zone.get("discount"):
                    buy_score += 4
                    reasons.append("Discount Zone")
                elif pd_zone.get("premium"):
                    sell_score += 4
                    warnings.append("Premium Zone")

            # -- Volume Profile POC
            vp = advanced_data.get("volume_profile")
            if vp and vp.get("poc") and vp.get("distance_to_poc", 100) < 2:
                buy_score += 3
                sell_score += 3
                reasons.append("Near POC")

            # -- VWAP
            vwap_data = advanced_data.get("vwap")
            if vwap_data and vwap_data.get("vwap"):
                if vwap_data["position"] == "above":
                    buy_score += 4
                    reasons.append("Price Above VWAP")
                elif vwap_data["position"] == "below":
                    sell_score += 4
                    warnings.append("Price Below VWAP")

            # -- Open Interest
            oi = advanced_data.get("open_interest")
            if oi and oi.get("state") not in ("unavailable", "unknown"):
                if oi["state"] == "Long Build Up":
                    buy_score += 4
                    reasons.append("OI Long Build Up")
                elif oi["state"] == "Short Build Up":
                    sell_score += 4
                    warnings.append("OI Short Build Up")
                elif oi["state"] == "Short Covering":
                    buy_score += 3
                    reasons.append("OI Short Covering")
                elif oi["state"] == "Long Unwinding":
                    sell_score += 3
                    warnings.append("OI Long Unwinding")

            # -- Funding Rate
            fr = advanced_data.get("funding_rate")
            if fr and fr.get("bias") != "unavailable":
                if fr["bias"] == "Bullish (Costly Longs)":
                    buy_score += 3
                    reasons.append("Funding Bullish Bias")
                elif fr["bias"] == "Bearish (Costly Shorts)":
                    sell_score += 3
                    warnings.append("Funding Bearish Bias")

            # -- ATR Volatility
            atr_vol = advanced_data.get("atr_volatility")
            if atr_vol:
                if atr_vol["volatility"] == "High Volatility":
                    buy_score -= 3
                    sell_score -= 3
                    warnings.append("High Volatility")
                elif atr_vol["volatility"] == "Low Volatility":
                    buy_score += 3
                    sell_score += 3
                    reasons.append("Low Volatility Contraction")

            # -- EMA Slope
            ema_slopes = advanced_data.get("ema_slope")
            if ema_slopes:
                if all(ema_slopes.get(f"EMA{p}_slope_pct", 0) > 0.1 for p in [20,50]):
                    buy_score += 4
                    reasons.append("EMA Slopes Positive")
                elif all(ema_slopes.get(f"EMA{p}_slope_pct", 0) < -0.1 for p in [20,50]):
                    sell_score += 4
                    warnings.append("EMA Slopes Negative")

            # -- RSI Divergence
            rsi_div = advanced_data.get("rsi_divergence")
            if rsi_div:
                if rsi_div.get("bullish_divergence"):
                    buy_score += 6
                    reasons.append("RSI Bullish Divergence")
                elif rsi_div.get("bearish_divergence"):
                    sell_score += 6
                    warnings.append("RSI Bearish Divergence")

            # -- MACD Divergence
            macd_div = advanced_data.get("macd_divergence")
            if macd_div:
                if macd_div.get("bullish_div"):
                    buy_score += 6
                    reasons.append("MACD Bullish Divergence")
                elif macd_div.get("bearish_div"):
                    sell_score += 6
                    warnings.append("MACD Bearish Divergence")

            # -- Candlestick Patterns
            cp = advanced_data.get("candlestick_patterns")
            if cp:
                if cp.get("engulfing_bullish") or cp.get("morning_star"):
                    buy_score += 4
                    reasons.append("Bullish Candlestick")
                elif cp.get("engulfing_bearish") or cp.get("evening_star"):
                    sell_score += 4
                    warnings.append("Bearish Candlestick")

            # -- SR Strength
            sr = advanced_data.get("sr_strength")
            if sr:
                if sr.get("valid_support"):
                    buy_score += 3
                    reasons.append("Strong Support")
                if sr.get("valid_resistance"):
                    sell_score += 3
                    warnings.append("Strong Resistance")

            # -- Breakout Quality
            bq = advanced_data.get("breakout_quality")
            if bq:
                if bq["quality"] == "Real Breakout":
                    buy_score += 7
                    reasons.append("Real Breakout")
                elif bq["quality"] == "Fake Breakout":
                    sell_score += 7
                    warnings.append("Fake Breakout")

            # -- Trendline Break
            tl = advanced_data.get("trendline_break")
            if tl and tl.get("trendline_break"):
                if tl["trendline_break"] == "bullish":
                    buy_score += 5
                    reasons.append("Bullish Trendline Break")
                elif tl["trendline_break"] == "bearish":
                    sell_score += 5
                    warnings.append("Bearish Trendline Break")

            # -- Fibonacci Golden Zone
            fib = advanced_data.get("fibonacci")
            if fib and fib.get("golden_zone"):
                low, high = fib["golden_zone"]
                if low <= last["close"] <= high:
                    buy_score += 3
                    sell_score += 3
                    reasons.append("Price in Golden Zone")

            # -- Session
            session = advanced_data.get("session")
            if session and session["session"] in ("London", "New York"):
                buy_score += 2
                sell_score += 2
                reasons.append(f"{session['session']} Session")

            # -- Market Regime
            regime = advanced_data.get("market_regime")
            if regime:
                if "Trending" in regime["regime"]:
                    buy_score += 6
                    sell_score += 6
                    reasons.append("Trending Market")
                elif "Ranging" in regime["regime"]:
                    buy_score -= 3
                    sell_score -= 3
                    warnings.append("Ranging/Choppy")

            # -- Correlation Filter
            corr = advanced_data.get("correlation")
            if corr and corr["btc_correlation"] is not None:
                if corr["btc_correlation"] > 0.7:
                    buy_score += 4
                    sell_score += 4
                    reasons.append("High BTC Correlation")

        # ========== News & Sentiment ==========
        # خبر مثبت به buy_score اضافه و از sell_score کم می‌کند (و برعکس)
        if news_score > 0:
            buy_score += news_score
            sell_score -= news_score
        elif news_score < 0:
            sell_score += abs(news_score)
            buy_score -= abs(news_score)

        if sentiment_score > 0:
            buy_score += sentiment_score
            sell_score -= sentiment_score
        elif sentiment_score < 0:
            sell_score += abs(sentiment_score)
            buy_score -= abs(sentiment_score)

        # ========== Strength Factor ==========
        if strength == "Weak":
            buy_score *= 0.8
            sell_score *= 0.8
        elif strength == "Medium":
            buy_score *= 0.9
            sell_score *= 0.9

        # محدودسازی ۰ تا ۱۰۰
        buy_score = max(0, min(100, buy_score))
        sell_score = max(0, min(100, sell_score))

        # ========== Base Score (برای نمایش) ==========
        base_score = max(buy_score, sell_score)

        # ========== Confidence ==========
        conf = 30
        if struct_trend in ("bullish", "bearish"):
            conf += 10
        if strength == "Very Strong":
            conf += 20
        elif strength == "Strong":
            conf += 15
        elif strength == "Medium":
            conf += 5
        else:
            conf -= 10
        # MTF alignment
        if buy_score > sell_score and "Bullish" in mtf_signal:
            conf += 15
        elif buy_score > sell_score and "Bearish" in mtf_signal:
            conf -= 10
        elif sell_score > buy_score and "Bearish" in mtf_signal:
            conf += 15
        elif sell_score > buy_score and "Bullish" in mtf_signal:
            conf -= 10
        if last_bos:
            if (buy_score > sell_score and last_bos["type"] == "bullish") or \
               (sell_score > buy_score and last_bos["type"] == "bearish"):
                conf += 10
        if opposing_choch:
            conf -= 20
        if vol_z > 0.5:
            conf += 10
        elif vol_z < -0.5:
            conf -= 5
        if breakout or breakdown:
            conf += 15
        if last["EMA20"] > last["EMA50"] and last["EMA50"] > last["EMA200"]:
            conf += 5
        if regime:
            if "Trending" in regime.get("regime", ""):
                conf += 10
            elif "Ranging" in regime.get("regime", ""):
                conf -= 5
        if rsi_div and rsi_div.get("bullish_divergence"):
            conf += 5
        if macd_div and macd_div.get("bullish_div"):
            conf += 5
        if atr_vol and atr_vol.get("volatility") == "High Volatility":
            conf -= 3
        if oi and oi.get("state") == "Long Unwinding":
            conf -= 2
        if macd_div and macd_div.get("bearish_div"):
            conf -= 4
        conf += news_score * 0.5 + sentiment_score * 0.3
        conf = max(10, min(100, conf))

        # دلایل و هشدارها
        reasons = list(dict.fromkeys(reasons))
        warnings = list(dict.fromkeys(warnings))

        weighted_reasons = []
        for r in reasons:
            weight = REASON_WEIGHTS.get(r, 1)
            stars = "★" * weight
            weighted_reasons.append(f"{stars} {r}")

        weighted_warnings = []
        for w in warnings:
            if w.startswith("Price Near Resistance"):
                lookup_key = "Price Near Resistance"
            else:
                lookup_key = w
            weight_tuple = WARNING_WEIGHTS.get(lookup_key, (1, "minor"))
            weight = weight_tuple[0] if isinstance(weight_tuple, tuple) else weight_tuple
            stars = "★" * weight
            weighted_warnings.append(f"{stars} {w}")

        return {
            "buy_score": int(round(buy_score)),
            "sell_score": int(round(sell_score)),
            "score": int(round(base_score)),
            "confidence": int(conf),
            "breakout": breakout,
            "reasons": reasons,
            "warnings": warnings,
            "weighted_reasons": weighted_reasons,
            "weighted_warnings": weighted_warnings,
            "strength": strength,
            "news_score": news_score,
            "sentiment_score": sentiment_score,
            "base_score": int(round(base_score)),
            "mtf_bonus": 0  # دیگر استفاده نمی‌شود
        }
