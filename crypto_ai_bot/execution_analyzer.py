"""
Crypto AI Bot v1.2
Liquidity-aware Execution Analyzer – Expanded Types, Realistic Quality
"""

import numpy as np

class ExecutionAnalyzer:
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
        if vwap_data and vwap_data.get("vwap"):
            dist_vwap = abs(entry_price - vwap_data["vwap"]) / entry_price
            if dist_vwap < 0.002: quality += 10
            elif dist_vwap > 0.02: quality -= 5

        liq_risk = 0
        swing_highs = market_structure.get("swing_highs", [])
        swing_lows = market_structure.get("swing_lows", [])
        if action in ("BUY", "STRONG BUY"):
            for low in swing_lows:
                if abs(entry_price - low) / entry_price < 0.005:
                    liq_risk += 10
                    quality -= 5
        elif action in ("SELL", "STRONG SELL"):
            for high in swing_highs:
                if abs(entry_price - high) / entry_price < 0.005:
                    liq_risk += 10
                    quality -= 5

        if advanced_data.get("order_block", {}).get("valid"): quality += 5
        if advanced_data.get("fvg", {}).get("active_fvg"): quality += 5
        if advanced_data.get("volume_profile", {}).get("poc"):
            if abs(entry_price - advanced_data["volume_profile"]["poc"]) / entry_price < 0.01:
                quality += 10

        quality = max(30, min(95, quality))

        if quality < 40 or liq_risk > 40:
            exec_type = "Avoid Trade"
        elif quality >= 85 and vol_z > 1.0:
            exec_type = "Market Order"
        elif quality >= 75:
            if action in ("BUY", "STRONG BUY"):
                if entry_price < vwap_data.get("vwap", entry_price):
                    exec_type = "Limit Near Support"
                else:
                    exec_type = "Limit Order"
            else:
                if entry_price > vwap_data.get("vwap", entry_price):
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
