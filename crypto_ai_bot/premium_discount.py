"""
Premium / Discount Zone
"""

class PremiumDiscount:
    @staticmethod
    def detect(df, market_structure=None):
        if market_structure is None:
            return {"zone": "equilibrium", "premium": False, "discount": False}
        highs = [h["price"] for h in market_structure.get("swing_highs", [])]
        lows = [l["price"] for l in market_structure.get("swing_lows", [])]
        if len(highs) < 2 or len(lows) < 2:
            return {"zone": "equilibrium", "premium": False, "discount": False}
        # محدوده نوسان از آخرین سویینگ‌ها
        range_high = max(highs[-2:])
        range_low = min(lows[-2:])
        current = df["close"].iloc[-1]
        if range_high == range_low:
            return {"zone": "equilibrium", "premium": False, "discount": False}
        ratio = (current - range_low) / (range_high - range_low)
        if ratio > 0.79:
            return {"zone": "premium", "premium": True, "discount": False}
        elif ratio < 0.21:
            return {"zone": "discount", "premium": False, "discount": True}
        elif 0.45 <= ratio <= 0.55:
            return {"zone": "equilibrium", "premium": False, "discount": False}
        else:
            return {"zone": "mid", "premium": False, "discount": False}
