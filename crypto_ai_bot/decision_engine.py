"""
Crypto AI Bot v1.1
Professional Decision Engine (Macro, News, Sentiment integrated)
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

        # Confidence
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
        conf += int(news_score * 2) + int(sentiment_score * 2)
        if risk_event: conf -= 15
        conf = max(10, min(100, conf))

        # Trade Readiness
        readiness = 50
        if trend == "bullish": readiness += 20
        elif trend == "bearish": readiness -= 20
        if strength == "Very Strong": readiness += 20
        elif strength == "Strong": readiness += 15
        elif strength == "Medium": readiness += 5
        if "Bullish" in mtf_signal: readiness += 15
        elif "Bearish" in mtf_signal: readiness -= 10
        if last_bos: readiness += 15
        if opposing_choch: readiness -= 20
        if vol_z > 0.5: readiness += 10
        if breakout: readiness += 15
        readiness += int(news_score) + int(sentiment_score)
        if risk_event: readiness -= 25
        readiness = max(0, min(100, readiness + score // 2))

        # Action
        if risk_event:
            action = "WATCH"
            decision_reason = "Macro Risk Active – High Impact news approaching."
        elif trend == "bearish":
            action = "NO TRADE"
            decision_reason = "Bearish trend."
        elif trend == "bullish" and last_bos and "Bullish" in mtf_signal and vol_z > 0.5 and not opposing_choch and news_score >= 0:
            if readiness >= 90 and conf >= 75:
                action = "STRONG BUY"
                decision_reason = "All conditions aligned: BOS, MTF, Volume, Positive News/Sentiment."
            elif readiness >= 75 and conf >= 60:
                action = "BUY"
                decision_reason = "Good setup, awaiting full confirmation."
            else:
                action = "WATCH"
                decision_reason = "Missing some confirmations."
        else:
            action = "WATCH"
            decision_reason = "Waiting for stronger signals."

        summary = {
            "Market Bias": "Bullish" if trend == "bullish" else "Bearish",
            "Current Status": decision_reason,
            "Decision Reason": decision_reason,
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
