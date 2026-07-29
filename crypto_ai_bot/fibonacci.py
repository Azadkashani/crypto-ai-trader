"""
Fibonacci Retracement
"""

class Fibonacci:
    @staticmethod
    def detect(df, market_structure=None):
        if market_structure is None:
            return {"levels": {}, "golden_zone": None}
        highs = [h["price"] for h in market_structure.get("swing_highs", [])]
        lows = [l["price"] for l in market_structure.get("swing_lows", [])]
        if len(highs) < 2 or len(lows) < 2:
            return {"levels": {}, "golden_zone": None}
        recent_high = max(highs[-2:])
        recent_low = min(lows[-2:])
        diff = recent_high - recent_low
        if diff == 0:
            return {"levels": {}, "golden_zone": None}
        levels = {
            "0.0": recent_low,
            "0.236": round(recent_low + 0.236 * diff, 4),
            "0.382": round(recent_low + 0.382 * diff, 4),
            "0.5": round(recent_low + 0.5 * diff, 4),
            "0.618": round(recent_low + 0.618 * diff, 4),
            "0.786": round(recent_low + 0.786 * diff, 4),
            "1.0": recent_high
        }
        golden_zone = (levels["0.618"], levels["0.786"])
        return {"levels": levels, "golden_zone": golden_zone}
