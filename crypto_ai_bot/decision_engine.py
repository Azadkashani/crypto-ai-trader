"""
Crypto AI Bot v1.2
Professional Decision Engine – Capped Confidence, Warning Penalties, Dynamic Readiness
"""

from weights import WARNING_WEIGHTS
from config import MIN_RISK_REWARD, MIN_EXECUTION_QUALITY, MIN_EXPECTED_VALUE

class DecisionEngine:
    @staticmethod
    def evaluate(df, market_structure, mtf_signal, strength, advanced_data,
                 buy_score, sell_score, breakout, reasons, warnings,
                 risk_event=False, news_score=0, sentiment_score=0,
                 plan_valid=True, ev=None, execution_quality=None, rr=None):
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

        # ---- Confidence (capped at 98) ----
        conf = 30
        if trend in ("bullish", "bearish"): conf += 10
        if strength == "Very Strong": conf += 20
        elif strength == "Strong": conf += 15
        elif strength == "Medium": conf += 5
        else: conf -= 10

        if buy_score > sell_score:
            if "Bullish" in mtf_signal: conf += 15
            elif "Bearish" in mtf_signal: conf -= 10
        elif sell_score > buy_score:
            if "Bearish" in mtf_signal: conf += 15
            elif "Bullish" in mtf_signal: conf -= 10

        if last_bos:
            if (buy_score > sell_score and last_bos["type"] == "bullish") or \
               (sell_score > buy_score and last_bos["type"] == "bearish"):
                conf += 10

        if opposing_choch: conf -= 20
        avg_vol = df["volume"].tail(20).mean()
        std_vol = df["volume"].tail(20).std()
        vol_z = (last["volume"] - avg_vol) / std_vol if std_vol != 0 else 0
        if vol_z > 0.5: conf += 10
        elif vol_z < -0.5: conf -= 5
        if breakout: conf += 15
        if last["EMA20"] > last["EMA50"] and last["EMA50"] > last["EMA200"]:
            conf += 5
        regime = advanced_data.get("market_regime") if advanced_data else None
        if regime:
            if "Trending" in regime.get("regime", ""): conf += 10
            elif "Ranging" in regime.get("regime", ""): conf -= 5
        rsi_div = advanced_data.get("rsi_divergence") if advanced_data else None
        macd_div = advanced_data.get("macd_divergence") if advanced_data else None
        if rsi_div and rsi_div.get("bullish_divergence"): conf += 5
        if macd_div and macd_div.get("bullish_div"): conf += 5
        atr_vol = advanced_data.get("atr_volatility") if advanced_data else None
        if atr_vol and atr_vol.get("volatility") == "High Volatility": conf -= 3
        oi = advanced_data.get("open_interest") if advanced_data else None
        if oi and oi.get("state") == "Long Unwinding": conf -= 2
        if macd_div and macd_div.get("bearish_div"): conf -= 4

        # Warning penalties
        warning_text = " ".join(warnings)
        if "Premium Zone" in warning_text or "Price Near Resistance" in warning_text:
            conf -= 5
        if "Bearish Divergence" in warning_text:
            conf -= 5

        conf += news_score * 0.5 + sentiment_score * 0.3
        conf = max(10, min(98, conf))   # cap at 98%

        # ---- Trade Readiness (dynamic) ----
        readiness = max(buy_score, sell_score)
        if execution_quality is not None:
            readiness = readiness * 0.6 + execution_quality * 0.2 + (confidence:=conf) * 0.2
        if ev is not None and ev > 0:
            readiness += 5
        if risk_event:
            readiness -= 10
        readiness = max(0, min(100, int(readiness)))

        # ---- Action اولیه ----
        if risk_event:
            action = "WATCH"
            decision_reason = "High impact macro event approaching."
        elif buy_score >= 85 and buy_score > sell_score:
            action = "STRONG BUY"
            decision_reason = "Exceptional long setup."
        elif buy_score >= 70 and buy_score > sell_score:
            action = "BUY"
            decision_reason = "Good long setup."
        elif sell_score >= 85 and sell_score > buy_score:
            action = "STRONG SELL"
            decision_reason = "Exceptional short setup."
        elif sell_score >= 70 and sell_score > buy_score:
            action = "SELL"
            decision_reason = "Good short setup."
        elif readiness >= 55:
            action = "WATCH"
            decision_reason = "Waiting for clearer direction."
        else:
            action = "NO TRADE"
            decision_reason = "No actionable signal."

        # ---- تصحیح با Trade Planner ----
        if action in ("BUY", "SELL", "STRONG BUY", "STRONG SELL"):
            if not plan_valid:
                action = "WATCH"
                decision_reason = "Trade plan invalid."
            elif ev is not None and ev <= MIN_EXPECTED_VALUE:
                action = "WATCH"
                decision_reason = f"Negative Expected Value ({ev}R)."
            elif execution_quality is not None and execution_quality < MIN_EXECUTION_QUALITY:
                action = "WATCH"
                decision_reason = f"Low execution quality ({execution_quality}%)."
            elif rr is not None and rr < MIN_RISK_REWARD:
                action = "WATCH"
                decision_reason = f"Risk/Reward too low ({rr:.2f} < {MIN_RISK_REWARD})"

        summary = {
            "Market Bias": "Bullish" if buy_score > sell_score else "Bearish" if sell_score > buy_score else "Sideways",
            "Current Status": decision_reason,
            "Decision Reason": decision_reason,
            "Missing": [],
            "Risk Level": "Medium"
        }

        print(f"[DecisionEngine v4.3] buy={buy_score} sell={sell_score} => {action}")
        return {
            "action": action,
            "confidence": conf,
            "trade_readiness": readiness,
            "entry_quality": "B+",
            "summary": summary,
        }
