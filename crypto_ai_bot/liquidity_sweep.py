"""
Liquidity Sweep Detection
"""

class LiquiditySweep:
    @staticmethod
    def detect(df, market_structure=None):
        if market_structure is None:
            return {"buy_side_sweep": False, "sell_side_sweep": False, "details": []}
        swings_high = market_structure.get("swing_highs", [])
        swings_low = market_structure.get("swing_lows", [])
        last_close = df["close"].iloc[-1]
        buy_sweep = False
        sell_sweep = False
        if swings_high:
            last_high = swings_high[-1]["price"]
            if df["high"].iloc[-1] > last_high and last_close < last_high:
                sell_sweep = True
        if swings_low:
            last_low = swings_low[-1]["price"]
            if df["low"].iloc[-1] < last_low and last_close > last_low:
                buy_sweep = True
        return {
            "buy_side_sweep": buy_sweep,
            "sell_side_sweep": sell_sweep,
            "details": {
                "last_high": swings_high[-1]["price"] if swings_high else None,
                "last_low": swings_low[-1]["price"] if swings_low else None,
                "current_high": df["high"].iloc[-1],
                "current_low": df["low"].iloc[-1],
                "close": last_close
            }
        }
