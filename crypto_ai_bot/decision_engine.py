"""
Crypto AI Bot v1.1
Professional Decision Engine (Balanced – Smart Action + Truly Dynamic Readiness v2)
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

        # ---- Confidence (بدون تغییر) ----
        conf = 30
        if trend == "bullish": conf += 10
        elif trend == "bearish": conf -= 10
        if strength == "Very Strong": conf += 20
        elif strength == "Strong": conf += 15
        elif strength == "Medium": conf += 5
        else: conf -= 10
        if "Bullish" in mtf_signal: conf += 15
        elif "Bearish" in mtf_signal: conf -= 10
        if last_bos: conf += 15
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

        # ---- Trade Readiness (کاملاً پویا و سخت‌گیرانه) ----
        readiness = 20   # پایهٔ پایین‌تر

        # روند
        if trend == "bullish":
            readiness += 15
        elif trend == "bearish":
            readiness -= 30
        else:
            readiness -= 15

        # قدرت روند
        if strength == "Very Strong": readiness += 10
        elif strength == "Strong": readiness += 7
        elif strength == "Medium": readiness += 3
        else: readiness -= 10

        # هم‌جهتی MTF
        if mtf_signal == "Strong Bullish": readiness += 10
        elif mtf_signal == "Bullish": readiness += 5
        elif mtf_signal == "Bearish": readiness -= 10
        elif mtf_signal == "Strong Bearish": readiness -= 20

        # BOS
        if last_bos:
            readiness += 10
        else:
            readiness -= 10

        # CHoCH مخالف
        if opposing_choch:
            readiness -= 20

        # حجم (تأثیر قوی‌تر)
        if vol_z > 0.5:
            readiness += 10
        elif vol_z < -0.5:
            readiness -= 15
        else:
            readiness -= 5   # حجم معمولی جریمه دارد

        # شکست
        if breakout:
            readiness += 10

        # News & Sentiment (تأثیر واقعی)
        if news_score > 0:
            readiness += min(int(news_score * 2), 10)
        elif news_score < -5:
            readiness -= 15

        if sentiment_score > 0:
            readiness += min(int(sentiment_score * 2), 10)
        elif sentiment_score < -5:
            readiness -= 10

        # Macro Risk
        if risk_event:
            readiness -= 30

        # سهم امتیاز تکنیکال (کاهش یافته)
        readiness += min(score // 5, 10)   # حداکثر ۱۰ امتیاز از Score

        readiness = max(0, min(100, readiness))

        # ---- Action اصلی ----
        critical_rejections = []
        if risk_event:
            critical_rejections.append("Macro Risk Active")
        if trend == "bearish":
            critical_rejections.append("Bearish Trend")
        if opposing_choch:
            critical_rejections.append("Opposing CHoCH")
        if news_score < -10:
            critical_rejections.append("Strong Negative News")

        if critical_rejections:
            action = "WATCH"
            decision_reason = "Blocked by: " + ", ".join(critical_rejections)
        elif trend == "bullish":
            if readiness >= 70 and conf >= 65:
                action = "STRONG BUY"
                decision_reason = "All conditions aligned strongly."
            elif readiness >= 55 and conf >= 50:
                action = "BUY"
                decision_reason = "Good setup with sufficient confirmation."
            else:
                action = "WATCH"
                decision_reason = "Waiting for stronger readiness/confidence."
        else:
            action = "WATCH"
            decision_reason = "Trend not clearly bullish."

        summary = {
            "Market Bias": "Bullish" if trend == "bullish" else "Bearish",
            "Current Status": decision_reason,
            "Decision Reason": decision_reason,
            "Missing": [],
            "Risk Level": "Medium"
        }
        print(f"[DecisionEngine v2.0] {trend} | Readiness={readiness} | Conf={conf}")   # تأیید نسخه
        return {
            "action": action,
            "confidence": conf,
            "trade_readiness": readiness,
            "entry_quality": "B+",
            "summary": summary,
        }
