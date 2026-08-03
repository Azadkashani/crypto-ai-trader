"""
Crypto AI Bot v1.1
Professional Decision Engine (Fully Symmetric for Long & Short)
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

        # ---- Confidence (متقارن) ----
        conf = 30
        if trend in ("bullish", "bearish"): conf += 10
        if strength == "Very Strong": conf += 20
        elif strength == "Strong": conf += 15
        elif strength == "Medium": conf += 5
        else: conf -= 10
        if (trend == "bullish" and "Bullish" in mtf_signal) or (trend == "bearish" and "Bearish" in mtf_signal):
            conf += 15
        elif (trend == "bullish" and "Bearish" in mtf_signal) or (trend == "bearish" and "Bullish" in mtf_signal):
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

        # ---- Trade Readiness (کاملاً قرینه برای خرید و فروش) ----
        readiness = 20

        # روند (برای هر دو جهت یکسان)
        if trend in ("bullish", "bearish"):
            readiness += 15
        else:
            readiness -= 15

        # قدرت روند
        if strength == "Very Strong": readiness += 10
        elif strength == "Strong": readiness += 7
        elif strength == "Medium": readiness += 3
        else: readiness -= 10

        # هم‌جهتی MTF (جهت‌دار)
        if (trend == "bullish" and "Bullish" in mtf_signal) or (trend == "bearish" and "Bearish" in mtf_signal):
            readiness += 10
        elif (trend == "bullish" and "Bearish" in mtf_signal) or (trend == "bearish" and "Bullish" in mtf_signal):
            readiness -= 10

        # BOS (جهت‌دار)
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

        # حجم (خنثی)
        if vol_z > 0.5:
            readiness += 10
        elif vol_z < -0.5:
            readiness -= 20
        else:
            readiness -= 10

        # شکست (جهت‌دار: در فروش، شکست حمایت مهم است)
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

        # سهم امتیاز تکنیکال (خنثی)
        readiness += min(score // 5, 15)

        # جریمه‌های ویژه – **قرینه‌سازی بر اساس جهت روند**
        # برای خرید: Discount خوب است، Premium بد
        # برای فروش: Premium خوب است، Discount بد
        if trend == "bullish":
            if "Premium Zone" in warnings or "Premium Zone" in str(warnings):
                readiness -= 5
            if "Discount Zone" in reasons or "Discount Zone" in str(reasons):
                readiness += 5
            if "Price Near Resistance" in str(warnings):
                readiness -= 10
            if "Strong Support" in reasons or "Strong Support" in str(reasons):
                readiness += 5
        elif trend == "bearish":
            if "Premium Zone" in warnings or "Premium Zone" in str(warnings):
                readiness += 5
            if "Discount Zone" in reasons or "Discount Zone" in str(reasons):
                readiness -= 5
            if "Price Near Resistance" in str(warnings):
                readiness += 10   # نزدیکی به مقاومت برای فروش خوب است (سقف)
            if "Strong Support" in reasons or "Strong Support" in str(reasons):
                readiness -= 5    # حمایت قوی برای فروش بد است

        # جریمه‌های OI (جهت‌دار)
        if "OI Long Unwinding" in warnings or "OI Long Unwinding" in str(warnings):
            readiness -= 8 if trend == "bullish" else 0
        if "OI Short Build Up" in warnings or "OI Short Build Up" in str(warnings):
            readiness -= 8 if trend == "bearish" else 0

        # کندل‌های جهت‌دار
        if "Bearish Candlestick" in warnings:
            readiness -= 5 if trend == "bullish" else 0
            readiness += 5 if trend == "bearish" else 0
        if "Bullish Candlestick" in reasons:
            readiness += 5 if trend == "bullish" else 0
            readiness -= 5 if trend == "bearish" else 0

        readiness = max(0, min(100, readiness))

        # ---- Action اصلی (آستانه‌های یکسان) ----
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
            if readiness >= 85 and conf >= 80:
                action = "STRONG BUY"
                decision_reason = "Exceptional long setup."
            elif readiness >= 70 and conf >= 60:
                action = "BUY"
                decision_reason = "Good long setup."
            elif readiness >= 55:
                action = "WATCH"
                decision_reason = "Long signal needs improvement."
            else:
                action = "NO TRADE"
                decision_reason = "Insufficient long conditions."
        elif trend == "bearish":
            if readiness >= 85 and conf >= 80:
                action = "STRONG SELL"
                decision_reason = "Exceptional short setup."
            elif readiness >= 70 and conf >= 60:
                action = "SELL"
                decision_reason = "Good short setup."
            elif readiness >= 55:
                action = "WATCH"
                decision_reason = "Short signal needs improvement."
            else:
                action = "NO TRADE"
                decision_reason = "Insufficient short conditions."
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
        print(f"[DecisionEngine v3.1] {trend} | Readiness={readiness} | Conf={conf}")
        return {
            "action": action,
            "confidence": conf,
            "trade_readiness": readiness,
            "entry_quality": "B+",
            "summary": summary,
        }
