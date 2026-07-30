"""
Crypto AI Bot
Professional Decision Engine (with News Risk)
"""

from weights import WARNING_WEIGHTS, CONFIDENCE_FACTORS, REASON_WEIGHTS


class DecisionEngine:
    @staticmethod
    def evaluate(df, market_structure, mtf_signal, strength, advanced_data, score, breakout,
                 reasons, warnings, risk_event=False):
        last = df.iloc[-1]
        trend = market_structure.get("trend", "sideways")
        bos = market_structure.get("bos", [])
        last_bos = bos[-1] if bos else None
        last_event = market_structure.get("last_event")
        opposing_choch = False
        if last_event and last_event["event"] == "choch":
            if (trend == "bullish" and last_event["type"] == "bearish") or \
               (trend == "bearish" and last_event["type"] == "bullish"):
                opposing_choch = True

        # -------------------------------
        # محاسبه Confidence (همانند قبل)
        # -------------------------------
        conf = 0
        if trend == "bullish":
            conf += CONFIDENCE_FACTORS["trend_bullish"]
        elif trend == "bearish":
            conf += CONFIDENCE_FACTORS["trend_bearish"]
        if strength == "Very Strong":
            conf += CONFIDENCE_FACTORS["strength_very_strong"]
        elif strength == "Strong":
            conf += CONFIDENCE_FACTORS["strength_strong"]
        elif strength == "Medium":
            conf += CONFIDENCE_FACTORS["strength_medium"]
        else:
            conf += CONFIDENCE_FACTORS["strength_weak"]
        if "Bullish" in mtf_signal:
            if "Strong" in mtf_signal:
                conf += CONFIDENCE_FACTORS["mtf_bullish_strong"]
            else:
                conf += CONFIDENCE_FACTORS["mtf_bullish"]
        elif "Bearish" in mtf_signal:
            if "Strong" in mtf_signal:
                conf += CONFIDENCE_FACTORS["mtf_bearish_strong"]
            else:
                conf += CONFIDENCE_FACTORS["mtf_bearish"]
        if last_bos:
            conf += CONFIDENCE_FACTORS["bos_present"]
        if last["EMA20"] > last["EMA50"] and last["EMA50"] > last["EMA200"]:
            conf += CONFIDENCE_FACTORS["ema_aligned"]
        avg_vol = df["volume"].tail(20).mean()
        std_vol = df["volume"].tail(20).std()
        vol_z = (last["volume"] - avg_vol) / std_vol if std_vol > 0 else 0
        if vol_z > 0.5:
            conf += CONFIDENCE_FACTORS["volume_high"]
        elif vol_z < -0.5:
            conf += CONFIDENCE_FACTORS["volume_low"]
        if breakout:
            conf += CONFIDENCE_FACTORS["breakout_real"]
        regime = advanced_data.get("market_regime") if advanced_data else None
        if regime:
            if "Trending" in regime.get("regime", ""):
                conf += CONFIDENCE_FACTORS["regime_trending"]
            elif "Ranging" in regime.get("regime", ""):
                conf += CONFIDENCE_FACTORS["regime_ranging"]
        rsi_div = advanced_data.get("rsi_divergence") if advanced_data else None
        macd_div = advanced_data.get("macd_divergence") if advanced_data else None
        if rsi_div and rsi_div.get("bullish_divergence"):
            conf += CONFIDENCE_FACTORS["divergence_bullish"]
        if macd_div and macd_div.get("bullish_div"):
            conf += CONFIDENCE_FACTORS["divergence_bullish"]
        if rsi_div and rsi_div.get("bearish_divergence"):
            conf += CONFIDENCE_FACTORS["divergence_bearish"]
        if macd_div and macd_div.get("bearish_div"):
            conf += CONFIDENCE_FACTORS["divergence_bearish"]
        if opposing_choch:
            conf += CONFIDENCE_FACTORS["opposing_choch"]
        atr_vol = advanced_data.get("atr_volatility") if advanced_data else None
        if atr_vol and atr_vol.get("volatility") == "High Volatility":
            conf += CONFIDENCE_FACTORS["high_volatility"]
        oi = advanced_data.get("open_interest") if advanced_data else None
        if oi and oi.get("state") == "Long Unwinding":
            conf += CONFIDENCE_FACTORS["oi_long_unwinding"]
        conf = max(10, min(100, conf))

        # -------------------------------
        # Trade Readiness (مستقل)
        # -------------------------------
        base_readiness = 50
        if trend == "bullish":
            base_readiness += 25
        elif trend == "bearish":
            base_readiness -= 25
        if strength == "Very Strong":
            base_readiness += 20
        elif strength == "Strong":
            base_readiness += 15
        elif strength == "Medium":
            base_readiness += 5
        else:
            base_readiness -= 10
        if "Bullish" in mtf_signal:
            base_readiness += 20
        elif "Bearish" in mtf_signal:
            base_readiness -= 15
        if breakout:
            base_readiness += 15
        if vol_z > 0.5:
            base_readiness += 10
        critical_penalty = 0
        major_penalty = 0
        minor_penalty = 0
        for w in warnings:
            weight, severity = WARNING_WEIGHTS.get(w, (1, "minor"))
            if severity == "critical":
                critical_penalty += weight * 3
            elif severity == "major":
                major_penalty += weight * 2
            else:
                minor_penalty += weight * 1
        base_readiness -= (critical_penalty + major_penalty + minor_penalty)
        readiness = max(0, min(100, int(base_readiness)))

        # -------------------------------
        # تصمیم‌گیری نهایی (با در نظر گرفتن ریسک رویداد)
        # -------------------------------
        has_critical = any(
            WARNING_WEIGHTS.get(w, (0, ""))[1] == "critical" for w in warnings
        )

        if risk_event:
            action = "WAIT NEWS"
            readiness = max(0, readiness - 20)
            conf = max(10, conf - 15)
        elif trend == "bearish":
            action = "NO TRADE"
        elif has_critical and readiness < 80:
            action = "NO TRADE"
        elif readiness >= 95:
            action = "BUY"
        elif readiness >= 80:
            action = "WATCH"
        elif readiness >= 60:
            action = "WAIT"
        else:
            action = "NO TRADE"

        # -------------------------------
        # Entry Quality
        # -------------------------------
        support_50 = df["low"].tail(50).min()
        resistance_50 = df["high"].tail(50).max()
        atr_val = last["ATR"] if last["ATR"] > 0 else 0.0001
        entry_price = last["close"]
        dist_res = (resistance_50 - entry_price) / atr_val
        dist_sup = (entry_price - support_50) / atr_val
        eq_score = 0
        if dist_res > 3:
            eq_score += 2
        elif dist_res > 1.5:
            eq_score += 1
        if dist_sup > 2:
            eq_score += 2
        elif dist_sup > 1:
            eq_score += 1
        rr = 2.0
        if rr >= 2:
            eq_score += 2
        elif rr >= 1.5:
            eq_score += 1
        if strength == "Very Strong":
            eq_score += 3
        elif strength == "Strong":
            eq_score += 2
        elif strength == "Medium":
            eq_score += 1
        if breakout:
            eq_score += 3
        if advanced_data:
            if advanced_data.get("liquidity_sweep", {}).get("buy_side_sweep"):
                eq_score += 2
            ob = advanced_data.get("order_block", {})
            if ob.get("valid") and ob.get("bullish_ob"):
                eq_score += 2
            if advanced_data.get("fvg", {}).get("bullish_fvg"):
                eq_score += 1
            vp = advanced_data.get("volume_profile", {})
            if vp.get("distance_to_poc", 100) < 2:
                eq_score += 1
        quality_map = {12: "A+", 10: "A", 8: "B+", 6: "B", 4: "C"}
        entry_quality = "D"
        for k, v in sorted(quality_map.items(), reverse=True):
            if eq_score >= k:
                entry_quality = v
                break

        # -------------------------------
        # توضیح تصمیم و وضعیت
        # -------------------------------
        if action in ("BUY", "STRONG BUY"):
            status = "Ready for Entry"
        elif action == "WATCH":
            status = "Waiting for Confirmation"
        elif action == "WAIT":
            status = "Avoid Entry – Wait for Better Conditions"
        elif action == "WAIT NEWS":
            status = "High-impact news approaching – Pause"
        else:
            status = "No Trade – Bearish or Critical Issues"

        missing = []
        if trend != "bullish":
            missing.append("Bullish Trend")
        if last_bos is None:
            missing.append("BOS Confirmation")
        if not ("Bullish" in mtf_signal):
            missing.append("MTF Alignment")
        if vol_z <= 0.5:
            missing.append("Higher Volume")
        if resistance_50 - last["close"] < 0.02 * last["close"]:
            missing.append("Clear Break of Resistance")
        if (rsi_div and rsi_div.get("bearish_divergence")) or (macd_div and macd_div.get("bearish_div")):
            missing.append("Clear Divergence Signal")
        if opposing_choch:
            missing.append("CHoCH Resolution")
        if risk_event:
            missing.append("Wait for economic news to pass")

        decision_reason = ""
        if action == "BUY":
            decision_reason = "Strong bullish alignment, high readiness and confidence."
        elif action == "WATCH":
            decision_reason = "Bullish structure present but awaiting volume/breakout confirmation."
        elif action == "WAIT":
            decision_reason = "Multiple warnings reduce readiness; safer to wait."
        elif action == "WAIT NEWS":
            decision_reason = "High impact news event imminent – trading paused."
        else:
            decision_reason = "Bearish trend or critical structure conflict."

        risk_level = "Medium"
        if atr_vol and atr_vol.get("volatility") == "High Volatility":
            risk_level = "High"
        elif strength in ("Very Strong", "Strong") and not opposing_choch and vol_z > 0:
            risk_level = "Low"
        else:
            risk_level = "Medium"

        summary = {
            "Market Bias": f"{'Strong ' if strength in ('Very Strong','Strong') else ''}Bullish" if trend == "bullish" else "Bearish",
            "Current Status": status,
            "Decision Reason": decision_reason,
            "Missing": missing,
            "Risk Level": risk_level,
        }

        return {
            "action": action,
            "confidence": conf,
            "trade_readiness": readiness,
            "entry_quality": entry_quality,
            "summary": summary,
        }
