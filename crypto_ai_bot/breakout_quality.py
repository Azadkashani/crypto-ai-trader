"""
Breakout Quality
"""

class BreakoutQuality:
    @staticmethod
    def detect(df):
        resistance = df["high"].tail(20).max()
        current_close = df["close"].iloc[-1]
        volume = df["volume"].iloc[-1]
        avg_volume = df["volume"].tail(20).mean()
        if current_close > resistance:
            if volume > avg_volume * 1.5:
                quality = "Real Breakout"
            else:
                quality = "Fake Breakout"
        else:
            quality = "No Breakout"
        return {"quality": quality}
