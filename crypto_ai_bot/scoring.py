"""
Crypto AI Bot v5.6
Advanced Scoring Engine (Balanced Confidence + Weighted Reasons)
"""

from config import BUY_SCORE, WATCH_SCORE
from weights import REASON_WEIGHTS, WARNING_WEIGHTS


class ScoringEngine:

    @staticmethod
    def calculate(df, mtf_signal="Neutral", market_structure=None, strength="Medium", advanced_data=None):
        last = df.iloc[-1]

        # ==================== محاسبه Score ====================
        score = 0.0
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

        # 1. Market Structure (بیشترین وزن)
        if struct_trend == "bullish":
            score += 7
            reasons.append("Market Structure Bullish")
        elif struct_trend == "bearish":
            score -= 7
            warnings.append("Market Structure Bearish")

        if last_bos:
            if last_bos["type"] == "bullish":
                score += 12
                reasons.append("BOS Bullish Break")
            else:
                score -= 12
                warnings.append("BOS Bearish Break")

        # 2. Multi Timeframe (وزن بالا)
        mtf_delta = 0
        if mtf_signal == "Strong Bullish":
            mtf_delta = 15
        elif mtf_signal == "Bullish":
            mtf_delta = 10
        elif mtf_signal == "Bearish":
            mtf_delta = -10
        elif mtf_signal == "Strong Bearish":
            mtf_delta = -15
        score += mtf_delta
        if "Bullish" in mtf_signal:
            reasons.append(f"MTF {mtf_signal}")
        elif "Bearish" in mtf_signal:
            warnings.append(f"MTF {mtf_signal}")

        # 3. EMA
        ema_score = 0
        if last["EMA20"] > last["EMA50"]:
            ema_score += 8
            reasons.append("EMA20 > EMA50")
        if last["EMA50"] > last["EMA200"]:
            ema_score += 8
            reasons.append("EMA50 > EMA200")
        score += ema_score

        # 4. ADX & DI
        if last["ADX"] >= 25:
            score += 8
            reasons.append("Strong ADX")
        if last["+DI"] > last["-DI"]:
            score += 5
            reasons.append("+DI > -DI")
        elif last["-DI"] > last["+DI"]:
            score -= 5
            warnings.append("Bearish DI")

        # 5. RSI
        rsi = last["RSI"]
        if 45 <= rsi <= 65:
            score += 8
            reasons.append("Healthy RSI")
        elif 65 < rsi <= 75 and last["ADX"] >= 25:
            score += 6
            reasons.append("Strong Momentum RSI")

        # 6. MACD
        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 8
            reasons.append("Bullish MACD")

        # 7. Volume (Z-Score)
        avg_vol = df["volume"].tail(20).mean()
        std_vol = df["volume"].tail(20).std()
        if std_vol > 0:
            vol_z = (last["volume"] - avg_vol) / std_vol
        else:
            vol_z = 0
        if vol_z > 0.5:
            score += 8
            reasons.append("High Volume")
        elif vol_z < -0.5:
            warnings.append("Low Volume")

        # 8. Volume Breakout
        resistance_20 = df["high"].tail(20).max()
        breakout = last["close"] > resistance_20 and last["volume"] > 1.2 * avg_vol
        if breakout:
            score += 8
            reasons.append("Volume Breakout")

        # 9. Resistance Proximity (فقط در صورت عدم شکست)
        distance_pct = (resistance_20 - last["close"]) / last["close"] * 100 if last["close"] > 0 else 100
        if not breakout and not (last_bos and last_bos["type"] == "bullish"):
            if distance_pct < 2.0:
                score -= 5
                warnings.append(f"Price Near Resistance ({distance_pct:.1f}%)")

        # 10. Opposing CHoCH
        if opposing_choch:
            score -= 8
            warnings.append("Opposing CHoCH (active)")

        # 11. Advanced Analytics با وزن‌های بهینه
        if advanced_data:
            # -- Liquidity Sweep (±5)
            ls = advanced_data.get("liquidity_sweep")
            if ls:
                if ls.get("buy_side_sweep"):
                    score += 5
                    reasons.append("Buy Side Liquidity Sweep")
                if ls.get("sell_side_sweep"):
                    score -= 5
                    warnings.append("Sell Side Liquidity Sweep")

            # -- FVG (±5)
            fvg = advanced_data.get("fvg")
            if fvg:
                if fvg.get("bullish_fvg"):
                    score += 5
                    reasons.append("Unfilled Bullish FVG")
                if fvg.get("bearish_fvg"):
                    score -= 5
                    warnings.append("Unfilled Bearish FVG")

            # -- Order Block (±6)
            ob = advanced_data.get("order_block")
            if ob and ob.get("valid"):
                if ob.get("bullish_ob"):
                    score += 6
                    reasons.append("Bullish Order Block")
                elif ob.get("bearish_ob"):
                    score -= 6
                    warnings.append("Bearish Order Block")

            # -- Premium/Discount (±4)
            pd_zone = advanced_data.get("premium_discount")
            if pd_zone:
                if pd_zone.get("discount"):
                    score += 4
                    reasons.append("Discount Zone")
                elif pd_zone.get("premium"):
                    score -= 4
                    warnings.append("Premium Zone")

            # -- Volume Profile POC (±3)
            vp = advanced_data.get("volume_profile")
            if vp and vp.get("poc") and vp.get("distance_to_poc", 100) < 2:
                score += 3
                reasons.append("Near POC")

            # -- VWAP (±4)
            vwap_data = advanced_data.get("vwap")
            if vwap_data and vwap_data.get("vwap"):
                if vwap_data["position"] == "above":
                    score += 4
                    reasons.append("Price Above VWAP")
                elif vwap_data["position"] == "below":
                    score -= 4
                    warnings.append("Price Below VWAP")

            # -- Open Interest (±4)
            oi = advanced_data.get("open_interest")
            if oi and oi.get("state") not in ("unavailable", "unknown"):
                if oi["state"] == "Long Build Up":
                    score += 4
                    reasons.append("OI Long Build Up")
                elif oi["state"] == "Short Build Up":
                    score -= 4
                    warnings.append("OI Short Build Up")
                elif oi["state"] == "Short Covering":
                    score += 3
                    reasons.append("OI Short Covering")
                elif oi["state"] == "Long Unwinding":
                    score -= 3
                    warnings.append("OI Long Unwinding")

            # -- Funding Rate (±3)
            fr = advanced_data.get("funding_rate")
            if fr and fr.get("bias") != "unavailable":
                if fr["bias"] == "Bullish (Costly Longs)":
                    score += 3
                    reasons.append("Funding Bullish Bias")
                elif fr["bias"] == "Bearish (Costly Shorts)":
                    score -= 3
                    warnings.append("Funding Bearish Bias")

            # -- ATR Volatility (±3)
            atr_vol = advanced_data.get("atr_volatility")
            if atr_vol:
                if atr_vol["volatility"] == "High Volatility":
                    score -= 3
                    warnings.append("High Volatility")
                elif atr_vol["volatility"] == "Low Volatility":
                    score += 3
                    reasons.append("Low Volatility Contraction")

            # -- EMA Slope (±4)
            ema_slopes = advanced_data.get("ema_slope")
            if ema_slopes:
                if all(ema_slopes.get(f"EMA{p}_slope_pct", 0) > 0.1 for p in [20,50]):
                    score += 4
                    reasons.append("EMA Slopes Positive")

            # -- RSI Divergence (±6)
            rsi_div = advanced_data.get("rsi_divergence")
            if rsi_div:
                if rsi_div.get("bullish_divergence"):
                    score += 6
                    reasons.append("RSI Bullish Divergence")
                elif rsi_div.get("bearish_divergence"):
                    score -= 6
                    warnings.append("RSI Bearish Divergence")

            # -- MACD Divergence (±6)
            macd_div = advanced_data.get("macd_divergence")
            if macd_div:
                if macd_div.get("bullish_div"):
                    score += 6
                    reasons.append("MACD Bullish Divergence")
                elif macd_div.get("bearish_div"):
                    score -= 6
                    warnings.append("MACD Bearish Divergence")

            # -- Candlestick Patterns (±4)
            cp = advanced_data.get("candlestick_patterns")
            if cp:
                if cp.get("engulfing_bullish") or cp.get("morning_star"):
                    score += 4
                    reasons.append("Bullish Candlestick")
                elif cp.get("engulfing_bearish") or cp.get("evening_star"):
                    score -= 4
                    warnings.append("Bearish Candlestick")

            # -- SR Strength (Support +3, Resistance -2)
            sr = advanced_data.get("sr_strength")
            if sr:
                if sr.get("valid_support"):
                    score += 3
                    reasons.append("Strong Support")
                if sr.get("valid_resistance"):
                    score -= 2
                    warnings.append("Strong Resistance")

            # -- Breakout Quality (±7)
            bq = advanced_data.get("breakout_quality")
            if bq:
                if bq["quality"] == "Real Breakout":
                    score += 7
                    reasons.append("Real Breakout")
                elif bq["quality"] == "Fake Breakout":
                    score -= 5
                    warnings.append("Fake Breakout")

            # -- Trendline Break (±5)
            tl = advanced_data.get("trendline_break")
            if tl and tl.get("trendline_break"):
                if tl["trendline_break"] == "bullish":
                    score += 5
                    reasons.append("Bullish Trendline Break")
                elif tl["trendline_break"] == "bearish":
                    score -= 5
                    warnings.append("Bearish Trendline Break")

            # -- Fibonacci Golden Zone (±3)
            fib = advanced_data.get("fibonacci")
            if fib and fib.get("golden_zone"):
                low, high = fib["golden_zone"]
                if low <= last["close"] <= high:
                    score += 3
                    reasons.append("Price in Golden Zone")

            # -- Session (±2)
            session = advanced_data.get("session")
            if session and session["session"] in ("London", "New York"):
                score += 2
                reasons.append(f"{session['session']} Session")

            # -- Market Regime (±6)
            regime = advanced_data.get("market_regime")
            if regime:
                if "Trending" in regime["regime"]:
                    score += 6
                    reasons.append("Trending Market")
                elif "Ranging" in regime["regime"]:
                    score -= 3
                    warnings.append("Ranging/Choppy")

            # -- Correlation Filter (±4)
            corr = advanced_data.get("correlation")
            if corr and corr["btc_correlation"] is not None:
                if corr["btc_correlation"] > 0.7:
                    score += 4
                    reasons.append("High BTC Correlation")

        # Base Score before strength factor
        base_score = score

        # Strength Factor
        if strength == "Weak":
            score *= 0.8
        elif strength == "Medium":
            score *= 0.9

        score = max(0, min(100, score))

        # ==================== محاسبه Confidence (متعادل‌تر) ====================
        conf = 0
        
        if struct_trend == "bullish":
            conf += 15
        elif struct_trend == "bearish":
            conf -= 15

        if strength == "Very Strong":
            conf += 25
        elif strength == "Strong":
            conf += 18
        elif strength == "Medium":
            conf += 10
        else:
            conf -= 10

        if "Bullish" in mtf_signal:
            conf += 15
        elif "Bearish" in mtf_signal:
            conf -= 10

        if vol_z > 0.5:
            conf += 10
        elif vol_z < -0.5:
            conf -= 3

        if breakout:
            conf += 15

        if last_bos:
            conf += 10

        if last["EMA20"] > last["EMA50"] and last["EMA50"] > last["EMA200"]:
            conf += 5

        if regime:
            if "Trending" in regime["regime"]:
                conf += 10
            elif "Ranging" in regime["regime"]:
                conf -= 5

        if rsi_div and rsi_div.get("bullish_divergence"):
            conf += 5
        if macd_div and macd_div.get("bullish_div"):
            conf += 5

        if opposing_choch:
            conf -= 5
        if atr_vol and atr_vol["volatility"] == "High Volatility":
            conf -= 3
        if oi and oi.get("state") == "Long Unwinding":
            conf -= 2
        if macd_div and macd_div.get("bearish_div"):
            conf -= 4

        conf = max(10, min(100, conf))

        # حذف دلایل تکراری
        reasons = list(dict.fromkeys(reasons))
        warnings = list(dict.fromkeys(warnings))

        # افزودن وزن‌ها به Reasons و Warnings (اصلاح‌شده برای ساختار جدید weights)
        weighted_reasons = []
        for r in reasons:
            weight = REASON_WEIGHTS.get(r, 1)
            stars = "★" * weight
            weighted_reasons.append(f"{stars} {r}")

        weighted_warnings = []
        for w in warnings:
            # استخراج وزن عددی از tuple (weight, severity)
            weight_tuple = WARNING_WEIGHTS.get(w, (1, "minor"))
            weight = weight_tuple[0] if isinstance(weight_tuple, tuple) else weight_tuple
            stars = "★" * weight
            weighted_warnings.append(f"{stars} {w}")

        return {
            "base_score": int(base_score),
            "mtf_bonus": int(mtf_delta),
            "score": int(round(score)),
            "confidence": int(conf),
            "breakout": breakout,
            "reasons": reasons,
            "warnings": warnings,
            "weighted_reasons": weighted_reasons,
            "weighted_warnings": weighted_warnings,
            "strength": strength
        }
