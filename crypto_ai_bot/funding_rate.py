"""
Funding Rate Analysis
"""

class FundingRate:
    @staticmethod
    def detect(symbol, exchange):
        try:
            funding = exchange.fetch_funding_rate(symbol)
            rate = funding["fundingRate"] * 100
            threshold = 0.1
            if rate > threshold:
                bias = "Bullish (Costly Longs)"
            elif rate < -threshold:
                bias = "Bearish (Costly Shorts)"
            else:
                bias = "Neutral"
            return {
                "rate": round(rate, 4),
                "bias": bias,
                "crowd_sentiment": "Longs pay Shorts" if rate > 0 else "Shorts pay Longs"
            }
        except Exception:
            return {"rate": 0, "bias": "unavailable"}
