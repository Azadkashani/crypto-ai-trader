"""
Crypto AI Bot v1.1
Market Sentiment per Symbol (Funding, OI, Fear & Greed)
"""

import requests
from config import FEAR_GREED_ENABLED, ALTERNATIVE_ME_API_URL

class MarketSentiment:
    @staticmethod
    def fetch_sentiment(exchange, symbol=None):
        data = {"fear_greed_index": 50, "funding_rate": 0, "oi_delta_pct": 0}

        if FEAR_GREED_ENABLED:
            try:
                resp = requests.get(ALTERNATIVE_ME_API_URL, timeout=5)
                fg_data = resp.json().get("data", [{}])[0]
                data["fear_greed_index"] = int(fg_data.get("value", 50))
            except:
                pass

        if exchange and symbol:
            try:
                funding = exchange.fetch_funding_rate(symbol)
                data["funding_rate"] = funding.get("fundingRate", 0) * 100
            except:
                pass
            try:
                oi = exchange.fetch_open_interest(symbol)
                data["oi_delta_pct"] = 0
            except:
                pass

        return data
