"""
Crypto AI Bot v1.1
Professional Decision Engine (Balanced – Smart Action + Dynamic Readiness + SELL Support)
"""

from weights import WARNING_WEIGHTS

class DecisionEngine:
    @staticmethod
    def evaluate(df, market_structure, mtf_signal, strength, advanced_data,
                 score, breakout, reasons, warnings, risk_event=False,
                 news_score=0, sentiment_score=0):
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

        # ---- Confidence (مانند قبل) ----
        conf = 30
        if trend == "bullish": conf += 10
        elif trend == "bearish": conf += 10      # برای فروش هم روند قوی مهم است
        if strength == "Very Strong": conf += 20
        elif strength == "Strong": conf += 15
        elif strength == "Medium": conf += 5
        else: conf -= 10
        if ("Bullish" in mtf_signal and trend == "bullish") or ("Bearish" in mtf_signal and trend == "bearish"):
            conf += 15
        elif ("Bearish" in mtf_signal and trend == "bullish") or ("Bullish" in mtf_signal and trend == "bearish"):
            conf -= 10
        if last_bos:
            if (trend == "bullish" and last_bos["type"] == "bullish") or (trend == "bearish" and last_bos["type"] == "bearish"):
                conf += 15
        if opposing_choch: conf -= 20
        avg_vol = df["volume"].tail(20).mean()
        std_vol = df["volume"].tail(20).std()
        vol_z = (last["volume"] - avg_vol) / std_vol if std_vol != 0 else 0
        if vol_z > 0.5: conf += 10
        if breakout: conf += 15
        if news_score < -5: conf -= 10
        if sentiment_score < -5: conf -= 5
        if risk_event: conf -= 15
        conf = max(10, min(100, conf))

        # ---- Trade Readiness (پویا و متقارن برای خرید/فروش) ----
        readiness = 20

        # روند
        if trend == "bullish" or trend == "bearish":
            readiness += 15
        else:
            readiness -= 15

        # قدرت روند
        if strength == "Very Strong": readiness += 10
        elif strength == "Strong": readiness += 7
        elif strength == "Medium": readiness += 3
        else: readiness -= 10

        # هم‌جهتی MTF
        if (trend == "bullish" and "Bullish" in mtf_signal) or (trend == "bearish" and "Bearish" in mtf_signal):
            readiness += 10
        elif (trend == "bullish" and "Bearish" in mtf_signal) or (trend == "bearish" and "Bullish" in mtf_signal):
            readiness -= 10

        # BOS
        if last_bos:
            if (trend == "bullish" and last_bos["type"] == "bullish") or (trend == "bearish" and last_bos["type"] == "bearish"):
                readiness += 10
            else:
                readiness -= 10
        else:
            readiness -= 10

        # CHoCH مخالف
        if opposing_choch:
            readiness -= 20

        # حجم
        if vol_z > 0.5:
            readiness += 10
        elif vol_z < -0.5:
            readiness -= 15
        else:
            readiness -= 5

        # شکست
        if breakout:
            readiness += 10

        # News & Sentiment (جهت‌دار)
        if trend == "bullish":
            if news_score > 0:
                readiness += min(int(news_score * 2), 10)
            elif news_score < -5:
                readiness -= 15
            if sentiment_score > 0:
                readiness += min(int(sentiment_score * 2), 10)
            elif sentiment_score < -5:
                readiness -= 10
        elif trend == "bearish":
            if news_score < 0:
                readiness += min(abs(int(news_score * 2)), 10)
            elif news_score > 5:
                readiness -= 15
            if sentiment_score < 0:
                readiness += min(abs(int(sentiment_score * 2)), 10)
            elif sentiment_score > 5:
                readiness -= 10

        # ریسک ماکرو
        if risk_event:
            readiness -= 30

        # سهم امتیاز تکنیکال
        readiness += min(score // 5, 10)

        readiness = max(0, min(100, readiness))

        # ---- Action اصلی ----
        critical_rejections = []
        if risk_event:
            critical_rejections.append("Macro Risk Active")
        if opposing_choch:
            critical_rejections.append("Opposing CHoCH")
        if (trend == "bullish" and news_score < -10) or (trend == "bearish" and news_score > 10):
            critical_rejections.append("Strong Contradictory News")

        if critical_rejections:
            action = "WATCH"
            decision_reason = "Blocked by: " + ", ".join(critical_rejections)
        elif trend == "bullish":
            if readiness >= 70 and conf >= 65:
                action = "STRONG BUY"
                decision_reason = "All conditions aligned strongly for long."
            elif readiness >= 55 and conf >= 50:
                action = "BUY"
                decision_reason = "Good setup for long."
            else:
                action = "WATCH"
                decision_reason = "Waiting for stronger long signal."
        elif trend == "bearish":
            if readiness >= 70 and conf >= 65:
                action = "STRONG SELL"
                decision_reason = "All conditions aligned strongly for short."
            elif readiness >= 55 and conf >= 50:
                action = "SELL"
                decision_reason = "Good setup for short."
            else:
                action = "WATCH"
                decision_reason = "Waiting for stronger short signal."
        else:
            action = "WATCH"
            decision_reason = "Trend not clearly directional."

        summary = {
            "Market Bias": "Bullish" if trend == "bullish" else "Bearish" if trend == "bearish" else "Sideways",
            "Current Status": decision_reason,
            "Decision Reason": decision_reason,
            "Missing": [],
            "Risk Level": "Medium"
        }
        print(f"[DecisionEngine v2.1] {trend} | Readiness={readiness} | Conf={conf}")
        return {
            "action": action,
            "confidence": conf,
            "trade_readiness": readiness,
            "entry_quality": "B+",
            "summary": summary,
        }
