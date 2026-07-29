"""
Support / Resistance Strength
"""

class SRStrength:
    @staticmethod
    def detect(df):
        resistance = df["high"].tail(50).max()
        support = df["low"].tail(50).min()
        touches_res = len(df.tail(50)[abs(df["high"] - resistance) / resistance < 0.005])
        touches_sup = len(df.tail(50)[abs(df["low"] - support) / support < 0.005])
        return {
            "resistance_level": resistance,
            "support_level": support,
            "resistance_touches": touches_res,
            "support_touches": touches_sup,
            "valid_resistance": touches_res >= 3,
            "valid_support": touches_sup >= 3
        }
