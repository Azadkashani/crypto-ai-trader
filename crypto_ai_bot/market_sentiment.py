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
                # قبلاً از fetch_open_interest فقط یک نقطه گرفته می‌شد و oi_delta_pct
                # همیشه 0 هاردکد بود. اینجا از تاریخچه استفاده می‌کنیم تا درصد تغییر واقعی محاسبه شود.
                oi_hist = exchange.fetch_open_interest_history(symbol, timeframe="1h", limit=2)
                if len(oi_hist) >= 2:
                    prev_oi = oi_hist[-2].get("openInterestAmount", 0)
                    curr_oi = oi_hist[-1].get("openInterestAmount", 0)
                    data["oi_delta_pct"] = ((curr_oi - prev_oi) / prev_oi) * 100 if prev_oi else 0
            except:
                pass

        return data
