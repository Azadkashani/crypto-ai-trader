"""
Crypto AI Bot v1.1
Professional Decision Engine (Strict STRONG BUY, Dynamic Readiness, Confidence aligned)
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

        # Confidence (هماهنگ با امتیاز)
        conf = 30
        if trend == "bullish":
            conf += 10
        elif trend == "bearish":
            conf -= 10
        if strength == "Very Strong":
            conf += 20
        elif strength == "Strong":
            conf += 15
        elif strength == "Medium":
            conf += 5
        else:
            conf -= 10
        if "Bullish" in mtf_signal:
            conf += 15
        elif "Bearish" in mtf_signal:
            conf -= 10
        if last_bos:
            conf += 15
        if opposing_choch:
            conf -= 20
        avg_vol = df["volume"].tail(20).mean()
        vol_z = (last["volume"] - avg_vol) / df["volume"].tail(20).std() if df["volume"].tail(20).std() != 0 else 0
        if vol_z > 0.5:
            conf += 10
        if breakout:
            conf += 15
        conf = max(10, min(100, conf + score // 2))

        # Trade Readiness (پویا)
        readiness = 50
        if trend == "bullish":
            readiness += 20
        elif trend == "bearish":
            readiness -= 20
        if strength == "Very Strong":
            readiness += 20
        elif strength == "Strong":
            readiness += 15
        elif strength == "Medium":
            readiness += 5
        if "Bullish" in mtf_signal:
            readiness += 15
        elif "Bearish" in mtf_signal:
            readiness -= 10
        if last_bos:
            readiness += 15
        if opposing_choch:
            readiness -= 20
        if vol_z > 0.5:
            readiness += 10
        if breakout:
            readiness += 15
        # News/Sentiment penalty
        if "news_score" in reasons or "news_score" in warnings:
            readiness += 5
        readiness = max(0, min(100, readiness + score // 2))

        # STRONG BUY فقط با شرایط کامل
        if trend == "bullish" and last_bos and "Bullish" in mtf_signal and vol_z > 0.5 and breakout and not opposing_choch:
            if readiness >= 90 and conf >= 75:
                action = "STRONG BUY"
            elif readiness >= 75 and conf >= 60:
                action = "BUY"
            else:
                action = "WATCH"
        elif trend == "bearish":
            action = "NO TRADE"
        else:
            action = "WATCH"

        summary = {
            "Market Bias": "Bullish" if trend == "bullish" else "Bearish",
            "Current Status": "Ready" if action in ("BUY", "STRONG BUY") else "Wait",
            "Decision Reason": "",
            "Missing": [],
            "Risk Level": "Medium"
        }
        return {
            "action": action,
            "confidence": conf,
            "trade_readiness": readiness,
            "entry_quality": "B+",
            "summary": summary,
        }
