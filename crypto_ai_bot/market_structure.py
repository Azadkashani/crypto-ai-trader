"""
Crypto AI Bot
Phase 1 - Step 1
Market Structure (Swing Engine)
"""

PIVOT_LENGTH = 5

class MarketStructure:

    @staticmethod
    def _is_pivot_high(df, i, length=PIVOT_LENGTH):
        if i < length or i >= len(df)-length:
            return False
        h = df["high"].iloc[i]
        return all(h > df["high"].iloc[j] for j in range(i-length, i)) and                all(h >= df["high"].iloc[j] for j in range(i+1, i+length+1))

    @staticmethod
    def _is_pivot_low(df, i, length=PIVOT_LENGTH):
        if i < length or i >= len(df)-length:
            return False
        l = df["low"].iloc[i]
        return all(l < df["low"].iloc[j] for j in range(i-length, i)) and                all(l <= df["low"].iloc[j] for j in range(i+1, i+length+1))

    @classmethod
    def analyze(cls, df):
        swing_highs = []
        swing_lows = []

        for i in range(len(df)):
            if cls._is_pivot_high(df, i):
                swing_highs.append({
                    "index": i,
                    "price": float(df["high"].iloc[i])
                })

            if cls._is_pivot_low(df, i):
                swing_lows.append({
                    "index": i,
                    "price": float(df["low"].iloc[i])
                })

        last_high = swing_highs[-1]["price"] if swing_highs else None
        last_low = swing_lows[-1]["price"] if swing_lows else None

        return {
            "swing_highs": swing_highs,
            "swing_lows": swing_lows,
            "last_high": last_high,
            "last_low": last_low,
        }
