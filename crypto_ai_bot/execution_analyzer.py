"""
Crypto AI Bot v1.2
Liquidity-aware Execution Analyzer
"""

import numpy as np

class ExecutionAnalyzer:
    @staticmethod
    def analyze(df, market_structure, advanced_data, action, entry_price):
        """
        تحلیل نقدینگی و پیشنهاد نوع اجرا به همراه امتیاز کیفیت.
        بازگشت: dict شامل execution_type, execution_quality, liquidity_risk
        """
        last = df.iloc[-1]
        atr = last["ATR"]
        avg_vol = df["volume"].tail(20).mean()
        std_vol = df["volume"].tail(20).std()
        vol_z = (last["volume"] - avg_vol) / std_vol if std_vol != 0 else 0

        # امتیاز کیفیت اولیه
        quality = 50

        # 1. حجم فعلی نسبت به میانگین
        if vol_z > 1.0:
            quality += 15
        elif vol_z > 0.5:
            quality += 10
        elif vol_z < -0.5:
            quality -= 10
        elif vol_z < -1.0:
            quality -= 20

        # 2. فاصله از VWAP
        vwap_data = advanced_data.get("vwap") if advanced_data else None
        if vwap_data and vwap_data.get("vwap"):
            dist_vwap = abs(entry_price - vwap_data["vwap"]) / vwap_data["vwap"]
            if dist_vwap < 0.005:  # نزدیک به VWAP (منطقه تعادل)
                quality += 10

        # 3. نزدیکی به استخرهای نقدینگی (Swing, OB, FVG)
        liq_risk = 0
        # Swing High/Low
        swing_highs = market_structure.get("swing_highs", [])
        swing_lows = market_structure.get("swing_lows", [])
        # اگر حد ضرر خیلی نزدیک به یک Swing Low (برای خرید) یا Swing High (برای فروش) باشد
        # (اینجا ساده‌سازی می‌کنیم)
        if action in ("BUY", "STRONG BUY"):
            for low in swing_lows:
                if abs(entry_price - low) / entry_price < 0.01:
                    liq_risk += 10
                    quality -= 5
        elif action in ("SELL", "STRONG SELL"):
            for high in swing_highs:
                if abs(entry_price - high) / entry_price < 0.01:
                    liq_risk += 10
                    quality -= 5

        # 4. شکاف FVG نزدیک
        fvg = advanced_data.get("fvg") if advanced_data else None
        if fvg and fvg.get("active_fvg"):
            gap = fvg["active_fvg"]
            gap_mid = (gap.get("gap_high", 0) + gap.get("gap_low", 0)) / 2
            if abs(entry_price - gap_mid) / entry_price < 0.01:
                quality += 10  # ورود در شکاف (نقدینگی خوب)

        # 5. وجود Order Block قوی
        ob = advanced_data.get("order_block") if advanced_data else None
        if ob and ob.get("valid"):
            quality += 10

        # 6. حجم پروفایل POC
        vp = advanced_data.get("volume_profile") if advanced_data else None
        if vp and vp.get("poc"):
            if abs(entry_price - vp["poc"]) / entry_price < 0.01:
                quality += 15  # ورود نزدیک POC (نقدینگی بالا)

        # تعیین نوع اجرا
        if quality < 30 or liq_risk > 30:
            execution_type = "Avoid Trade"
        elif quality >= 80 and vol_z > 1.0:
            execution_type = "Market Order"
        elif quality >= 70:
            if action in ("BUY", "STRONG BUY"):
                if entry_price < vwap_data.get("vwap", entry_price):
                    execution_type = "Limit Near Support"
                else:
                    execution_type = "Limit Order"
            else:  # sell
                if entry_price > vwap_data.get("vwap", entry_price):
                    execution_type = "Limit Near Resistance"
                else:
                    execution_type = "Limit Order"
        elif quality >= 50:
            execution_type = "Wait For Confirmation"
        else:
            execution_type = "Wait For Confirmation"

        # محدودسازی
        quality = max(0, min(100, quality))

        return {
            "execution_type": execution_type,
            "execution_quality": quality,
            "liquidity_risk": liq_risk
        }
