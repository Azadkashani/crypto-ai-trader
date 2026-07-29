"""
Crypto AI Bot v5.6
Advanced Scoring Engine (Calibrated)
"""

from config import BUY_SCORE, WATCH_SCORE


class ScoringEngine:

    @staticmethod
    def calculate(df, mtf_signal="Neutral", market_structure=None):
        last = df.iloc[-1]

        score = 0
        confidence = 50.0        # پایه ۵۰٪

        reasons = []
        warnings = []

        breakout = False

        # ==========================
        # Market Structure
        # ==========================
        struct_trend = "sideways"
        if market_structure is not None:
            struct_trend = market_structure.get("trend", "sideways")
            swing_highs = market_structure.get("swing_highs", [])
            swing_lows = market_structure.get("swing_lows", [])
            bos = market_structure.get("bos", [])
            choch = market_structure.get("choch", [])

            # روند ساختاری
            if struct_trend == "bullish":
                score += 5
                confidence += 5
                reasons.append("Market Structure Bullish")
            elif struct_trend == "bearish":
                score -= 5
                confidence -= 5
                warnings.append("Market Structure Bearish")

            # توصیف الگوی ساختاری (HH+HL یا LH+LL)
            pattern_reason = None
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                last_hh = swing_highs[-2]["label"]
                last_ll = swing_lows[-2]["label"]
                if struct_trend == "bullish" and last_hh == "HH" and last_ll == "HL":
                    pattern_reason = "Bullish Structure (HH+HL)"
                elif struct_trend == "bearish" and last_hh == "LH" and last_ll == "LL":
                    pattern_reason = "Bearish Structure (LH+LL)"

            # در صورت وجود الگو، همان را نمایش بده، در غیر این صورت سعی کن از آخرین لیبل‌ها کمک بگیری
            if pattern_reason:
                if struct_trend == "bullish":
                    reasons.append(pattern_reason)
                else:
                    warnings.append(pattern_reason)
            else:
                # نمایش آخرین لیبل‌ها به صورت جداگانه (فقط یکی)
                if swing_highs:
                    label_h = swing_highs[-1]["label"]
                    if struct_trend == "bullish" and label_h == "HH":
                        reasons.append("Higher High")
                    elif struct_trend == "bearish" and label_h == "LH":
                        warnings.append("Lower High")
                if swing_lows:
                    label_l = swing_lows[-1]["label"]
                    if struct_trend == "bullish" and label_l == "HL":
                        reasons.append("Higher Low")
                    elif struct_trend == "bearish" and label_l == "LL":
                        warnings.append("Lower Low")

            # BOS / CHoCH (آخرین رویداد)
            all_events = []
            for ev in bos:
                all_events.append({**ev, "event": "bos"})
            for ev in choch:
                all_events.append({**ev, "event": "choch"})
            if all_events:
                all_events.sort(key=lambda x: x["index"])
                last_event = all_events[-1]
                if last_event["event"] == "choch":
                    if last_event["type"] == "bullish":
                        if struct_trend == "bearish":
                            score -= 3      # جریمه تضاد
                            confidence -= 4
                            warnings.append("CHoCH Bullish (Potential Reversal)")
                        else:
                            # هم‌جهت با روند صعودی
                            score += 2
                            confidence += 2
                            reasons.append("CHoCH Bullish Confirmation")
                    else:  # bearish choch
                        if struct_trend == "bullish":
                            score -= 3
                            confidence -= 4
                            warnings.append("CHoCH Bearish (Potential Reversal)")
                        else:
                            score += 2
                            confidence += 2
                            reasons.append("CHoCH Bearish Confirmation")
                else:  # bos
                    if last_event["type"] == "bullish":
                        score += 8
                        confidence += 8
                        reasons.append("BOS Bullish Break")
                    else:
                        score -= 8
                        confidence -= 8
                        warnings.append("BOS Bearish Break")

        # ==========================
        # اندیکاتورهای کلاسیک
        # ==========================
        ema_bonus = 0
        if last["EMA20"] > last["EMA50"]:
            ema_bonus += 10
            reasons.append("EMA20 > EMA50")
        if last["EMA50"] > last["EMA200"]:
            ema_bonus += 10
            reasons.append("EMA50 > EMA200")
        score += ema_bonus
        confidence += ema_bonus * 0.5

        adx_bonus = 0
        if last["ADX"] >= 25:
            adx_bonus = 10
            score += adx_bonus
            confidence += adx_bonus * 0.5
            reasons.append("Strong ADX Trend")
        elif last["ADX"] < 15:
            warnings.append("Weak Trend")

        if last["+DI"] > last["-DI"]:
            score += 5
            confidence += 2
            reasons.append("+DI > -DI")
        elif last["-DI"] > last["+DI"]:
            score -= 3
            confidence -= 2
            warnings.append("Bearish DI")

        if last["MACD"] > last["MACD_SIGNAL"]:
            score += 10
            confidence += 5
            reasons.append("Bullish MACD")

        rsi = last["RSI"]
        if 45 <= rsi <= 65:
            score += 10
            confidence += 5
            reasons.append("Healthy RSI")
        elif 65 < rsi <= 75:
            if last["ADX"] >= 25:
                score += 7
                confidence += 3
                reasons.append("Strong Momentum RSI")
            else:
                warnings.append("High RSI")
        elif rsi < 30:
            score += 3
            reasons.append("Oversold RSI")
        elif rsi > 75:
            warnings.append("Overbought RSI")

        volume_bonus = 0
        if last["volume"] > last["AVG_VOLUME"]:
            volume_bonus = 10
            score += volume_bonus
            confidence += 5
            reasons.append("High Volume")

        # Volume Breakout
        resistance = df["high"].tail(50).max()
        if last["close"] > resistance and last["volume"] > last["AVG_VOLUME"]:
            breakout = True
            score += 5
            confidence += 3
            reasons.append("Volume Breakout")

        # ==========================
        # Base Score
        # ==========================
        base_score = score

        # ==========================
        # Multi Timeframe
        # ==========================
        mtf_delta = 0
        if mtf_signal == "Strong Bullish":
            mtf_delta = 10
            confidence += 5
            reasons.append("Strong Multi Timeframe")
        elif mtf_signal == "Bullish":
            mtf_delta = 5
            confidence += 3
            reasons.append("Bullish Multi Timeframe")
        elif mtf_signal == "Bearish":
            mtf_delta = -5
            confidence -= 3
            warnings.append("Bearish Multi Timeframe")
        elif mtf_signal == "Strong Bearish":
            mtf_delta = -10
            confidence -= 5
            warnings.append("Strong Bearish Multi Timeframe")

        score += mtf_delta

        # ==========================
        # هم‌جهتی ساختار با MTF (با کاهش وزن)
        # ==========================
        alignment_bonus = 0
        if struct_trend == "bullish" and "Bullish" in mtf_signal:
            alignment_bonus = 3
            reasons.append("Structure & MTF Alignment")
        elif struct_trend == "bearish" and "Bearish" in mtf_signal:
            alignment_bonus = -3
            warnings.append("Structure & MTF Alignment Bearish")
        score += alignment_bonus
        confidence += alignment_bonus * 0.5

        # ==========================
        # تناقض Trend و MTF
        # ==========================
        if struct_trend == "bullish" and ("Bearish" in mtf_signal):
            conflict_penalty = 8
            score -= conflict_penalty
            confidence -= 7
            warnings.append("Structure-MTF Conflict (Bullish vs Bearish)")
        elif struct_trend == "bearish" and ("Bullish" in mtf_signal):
            conflict_penalty = 8
            score -= conflict_penalty
            confidence -= 7
            warnings.append("Structure-MTF Conflict (Bearish vs Bullish)")

        # ==========================
        # محدودسازی Confidence بر اساس قدرت روند
        # ==========================
        # strength از بیرون اعمال می‌شود (در scanner). اینجا مستقیماً نداریم،
        # ولی می‌توانیم از ADX و حجم برای تخمین قدرت استفاده کنیم.
        # فعلاً از strength خبر نداریم؛ scanner بعداً اعمال می‌کند.
        # در اینجا صرفاً confidence را محدود به ۱۰-۹۰ می‌کنیم.
        if confidence > 90:
            confidence = 90
        elif confidence < 10:
            confidence = 10

        # Score هم محدود به 0-100
        if score > 100:
            score = 100
        elif score < 0:
            score = 0

        return {
            "base_score": base_score,
            "mtf_bonus": mtf_delta,
            "score": score,
            "confidence": confidence,
            "breakout": breakout,
            "reasons": reasons,
            "warnings": warnings
        }

    @staticmethod
    def action(score, breakout=False):
        if breakout and score >= WATCH_SCORE:
            return "BUY BREAKOUT"
        if score >= BUY_SCORE:
            return "BUY"
        if score >= WATCH_SCORE:
            return "WATCH"
        return "NO TRADE"
