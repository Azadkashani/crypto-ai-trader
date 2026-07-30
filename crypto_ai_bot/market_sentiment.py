"""
Crypto AI Bot
Market Sentiment Engine
"""

import requests
from config import ALTERNATIVE_ME_API_URL, FEAR_GREED_ENABLED

class MarketSentiment:
    @staticmethod
    def fetch_sentiment(exchange=None):
        data = {}
        # Fear & Greed
        if FEAR_GREED_ENABLED:
            try:
                resp = requests.get(ALTERNATIVE_ME_API_URL, timeout=10)
                fg_data = resp.json().get("data", [{}])[0]
                data["fear_greed_index"] = int(fg_data.get("value", 50))
                data["fear_greed_classification"] = fg_data.get("value_classification", "Neutral")
            except:
                data["fear_greed_index"] = 50

        # Funding Rate (از صرافی داده می‌شود)
        if exchange:
            try:
                funding = exchange.fetch_funding_rate("BTC/USDT")
                data["funding_rate"] = funding.get("fundingRate", 0) * 100
            except:
                data["funding_rate"] = 0

        # Open Interest delta (نمونه)
        if exchange:
            try:
                oi = exchange.fetch_open_interest("BTC/USDT")
                data["open_interest"] = oi.get("openInterestAmount", 0)
            except:
                data["open_interest"] = 0

        return data
