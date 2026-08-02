"""
Crypto AI Bot v1.1
Market Sentiment per Symbol (Funding, OI change, Fear & Greed)
"""

import requests
from config import FEAR_GREED_ENABLED, ALTERNATIVE_ME_API_URL

class MarketSentiment:
    @staticmethod
    def fetch_sentiment(exchange, symbol=None):
        data = {"fear_greed_index": 50, "funding_rate": 0, "oi_delta_pct": 0}

        # Fear & Greed (کل بازار)
        if FEAR_GREED_ENABLED:
            try:
                resp = requests.get(ALTERNATIVE_ME_API_URL, timeout=5)
                fg_data = resp.json().get("data", [{}])[0]
                data["fear_greed_index"] = int(fg_data.get("value", 50))
            except:
                pass

        if exchange and symbol:
            # Funding Rate
            try:
                funding = exchange.fetch_funding_rate(symbol)
                data["funding_rate"] = funding.get("fundingRate", 0) * 100
            except:
                pass

            # محاسبهٔ واقعی درصد تغییر OI
            try:
                oi_hist = exchange.fetch_open_interest_history(symbol, timeframe="1h", limit=2)
                if len(oi_hist) == 2:
                    prev_oi = float(oi_hist[0]["openInterestAmount"])
                    curr_oi = float(oi_hist[1]["openInterestAmount"])
                    if prev_oi != 0:
                        data["oi_delta_pct"] = ((curr_oi - prev_oi) / prev_oi) * 100
            except:
                pass

        return data
