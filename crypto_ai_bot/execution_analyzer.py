"""
Crypto AI Bot v1.2
Liquidity-aware Execution Analyzer – Safe float extraction
"""

import numpy as np

class ExecutionAnalyzer:

    @staticmethod
    def _safe_float(value):
        """همان تابع safe_float از TradePlanner"""
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

        quality = 50
        if vol_z > 1.5: quality += 20
        elif vol_z > 0.5: quality += 10
        elif vol_z < -0.5: quality -= 10
        elif vol_z < -1.5: quality -= 20

        if spread_est < 0.001: quality += 10
        elif spread_est > 0.01: quality -= 10

        vwap_data = advanced_data.get("vwap") if advanced_data else None
        vwap_price = ExecutionAnalyzer._safe_float(vwap_data.get("vwap")) if vwap_data else None
        if vwap_price:
            dist_vwap = abs(entry_price - vwap_price) / entry_price
            if dist_vwap < 0.002: quality += 10
            elif dist_vwap > 0.02: quality -= 5

        liq_risk = 0
        swing_highs = market_structure.get("swing_highs", [])
        swing_lows  = market_structure.get("swing_lows", [])

        if action in ("BUY", "STRONG BUY"):
            for low in swing_lows:
                low_val = ExecutionAnalyzer._safe_float(low)
                if low_val is not None and abs(entry_price - low_val) / entry_price < 0.005:
                    liq_risk += 10
                    quality -= 5
        elif action in ("SELL", "STRONG SELL"):
            for high in swing_highs:
                high_val = ExecutionAnalyzer._safe_float(high)
                if high_val is not None and abs(entry_price - high_val) / entry_price < 0.005:
                    liq_risk += 10
                    quality -= 5

        # OB, FVG, POC bonuses
        ob = advanced_data.get("order_block") if advanced_data else None
        if ob and ob.get("valid"):
            quality += 5

        fvg = advanced_data.get("fvg") if advanced_data else None
        if fvg and fvg.get("active_fvg"):
            quality += 5

        vp = advanced_data.get("volume_profile") if advanced_data else None
        if vp:
            poc_val = ExecutionAnalyzer._safe_float(vp.get("poc"))
            if poc_val is not None and abs(entry_price - poc_val) / entry_price < 0.01:
                quality += 10

        quality = max(30, min(95, quality))

        # Execution type selection
        if quality < 40 or liq_risk > 40:
            exec_type = "Avoid Trade"
        elif quality >= 85 and vol_z > 1.0:
            exec_type = "Market Order"
        elif quality >= 75:
            if action in ("BUY", "STRONG BUY"):
                if vwap_price and entry_price < vwap_price:
                    exec_type = "Limit Near Support"
                else:
                    exec_type = "Limit Order"
            else:
                if vwap_price and entry_price > vwap_price:
                    exec_type = "Limit Near Resistance"
                else:
                    exec_type = "Limit Order"
        elif quality >= 60:
            exec_type = "Wait For Confirmation"
        else:
            exec_type = "Reduce Position Size"

        return {
            "execution_type": exec_type,
            "execution_quality": quality,
            "liquidity_risk": liq_risk
        }
