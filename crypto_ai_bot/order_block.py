"""
Order Block Detection
"""

class OrderBlock:
    @staticmethod
    def detect(df, market_structure=None):
        if len(df) < 5:
            return {"bullish_ob": None, "bearish_ob": None, "valid": False, "touches": 0}
        # ساده: آخرین کندل صعودی/نزولی قوی قبل از شکست Swing
        bos = market_structure.get("bos", []) if market_structure else []
        if not bos:
            return {"bullish_ob": None, "bearish_ob": None, "valid": False, "touches": 0}
        last_bos = bos[-1]
        bos_idx = last_bos["index"]
        # کندل قبل از BOS
        if bos_idx > 0:
            ob_candle = df.iloc[bos_idx - 1]
            if last_bos["type"] == "bullish" and ob_candle["close"] < ob_candle["open"]:
                # bearish candle -> bullish OB
                return {"bullish_ob": None, "bearish_ob": {"high": ob_candle["high"], "low": ob_candle["low"]}, "valid": True, "touches": 0}
            elif last_bos["type"] == "bearish" and ob_candle["close"] > ob_candle["open"]:
                return {"bullish_ob": {"high": ob_candle["high"], "low": ob_candle["low"]}, "bearish_ob": None, "valid": True, "touches": 0}
        return {"bullish_ob": None, "bearish_ob": None, "valid": False, "touches": 0}
