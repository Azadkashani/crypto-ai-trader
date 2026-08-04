"""
Crypto AI Bot v1.2
Liquidity-aware Execution Analyzer – Wider Distribution, More Types
"""

import numpy as np

class ExecutionAnalyzer:

    @staticmethod
    def _safe_float(value):
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, dict):
            for key in ("price", "value", "close", "open", "high", "low"):
                if key in value:
                    return ExecutionAnalyzer._safe_float(value[key])
            for v in value.values():
                res = ExecutionAnalyzer._safe_float(v)
                if res is not None:
                    return res
            return None
        if isinstance(value, (list, tuple)):
            for item in value:
                res = ExecutionAnalyzer._safe_float(item)
                if res is not None:
                    return res
            return None
        try:
            return float(value)
        except:
            return None

    @staticmethod
    def analyze(df, market_structure, advanced_data, action, entry_price):
        last = df.iloc[-1]
        atr = last["ATR"]
        avg_vol = df["volume"].tail(20).mean()
        std_vol = df["volume"].tail(20).std()
        vol_z = (last["volume"] - avg_vol) / std_vol if std_vol != 0 else 0
        spread_est = atr / entry_price if entry_price else 0.001

        # امتیاز پایه‌ی پایین‌تر برای تنوع
        quality = 30

        # حجم
        if vol_z > 2.0: quality += 25
        elif vol_z > 1.0: quality += 15
        elif vol_z > 0.5: quality += 5
        elif vol_z < -0.5: quality -= 10
        elif vol_z < -1.5: quality -= 20

        # اسپرد
        if spread_est < 0.0005: quality += 20
        elif spread_est < 0.001: quality += 10
        elif spread_est > 0.01: quality -= 10

        # فاصله از VWAP
        vwap_data = advanced_data.get("vwap") if advanced_data else None
        vwap_price = ExecutionAnalyzer._safe_float(vwap_data.get("vwap")) if vwap_data else None
        if vwap_price:
            dist_vwap = abs(entry_price - vwap_price) / entry_price
            if dist_vwap < 0.002: quality += 15
            elif dist_vwap < 0.01: quality += 5
            elif dist_vwap > 0.03: quality -= 5

        # ریسک نقدینگی (Swing High/Low)
        liq_risk = 0
        swing_highs = market_structure.get("swing_highs", [])
        swing_lows  = market_structure.get("swing_lows", [])
        if action in ("BUY", "STRONG BUY"):
            for low in swing_lows:
                low_val = ExecutionAnalyzer._safe_float(low)
                if low_val is not None and abs(entry_price - low_val) / entry_price < 0.005:
                    liq_risk += 15
                    quality -= 10
        elif action in ("SELL", "STRONG SELL"):
            for high in swing_highs:
                high_val = ExecutionAnalyzer._safe_float(high)
                if high_val is not None and abs(entry_price - high_val) / entry_price < 0.005:
                    liq_risk += 15
                    quality -= 10

        # OB, FVG, POC
        if advanced_data.get("order_block", {}).get("valid"):
            quality += 8
        if advanced_data.get("fvg", {}).get("active_fvg"):
            quality += 8
        vp = advanced_data.get("volume_profile")
        if vp:
            poc_val = ExecutionAnalyzer._safe_float(vp.get("poc"))
            if poc_val is not None and abs(entry_price - poc_val) / entry_price < 0.01:
                quality += 12

        # سشن
        session = advanced_data.get("session", {}).get("session", "")
        if session in ("London", "New York", "London+NY Overlap"):
            quality += 5
        elif session == "Asia":
            quality -= 5

        quality = max(10, min(95, quality))

        # انتخاب نوع اجرا
        if quality < 30 or liq_risk > 50:
            exec_type = "Avoid Trade"
        elif quality >= 85 and vol_z > 1.0:
            if spread_est < 0.0005:
                exec_type = "Market Order"
            else:
                exec_type = "TWAP"
        elif quality >= 80 and spread_est < 0.001:
            exec_type = "Aggressive Limit"
        elif quality >= 75:
            if vwap_price and action in ("BUY", "STRONG BUY") and entry_price < vwap_price:
                exec_type = "Limit Near Support"
            elif vwap_price and action in ("SELL", "STRONG SELL") and entry_price > vwap_price:
                exec_type = "Limit Near Resistance"
            elif vwap_price and abs(entry_price - vwap_price)/entry_price < 0.005:
                exec_type = "VWAP Execution"
            elif spread_est > 0.005:
                exec_type = "Passive Limit"
            else:
                exec_type = "Limit Order"
        elif quality >= 60:
            exec_type = "Scale In"
        elif quality >= 45:
            exec_type = "Wait For Confirmation"
        else:
            exec_type = "Reduce Position Size"

        return {
            "execution_type": exec_type,
            "execution_quality": quality,
            "liquidity_risk": liq_risk
        }
