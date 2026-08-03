"""
Crypto AI Bot v1.2
Market Sentiment – Global + Asset Specific
"""

import requests
from config import FEAR_GREED_ENABLED, ALTERNATIVE_ME_API_URL

class MarketSentiment:
    @staticmethod
    def fetch_global_sentiment():
        """شاخص‌های کل بازار (Fear & Greed)"""
        data = {"fear_greed_index": 50}
        if FEAR_GREED_ENABLED:
            try:
                resp = requests.get(ALTERNATIVE_ME_API_URL, timeout=5)
                fg_data = resp.json().get("data", [{}])[0]
                data["fear_greed_index"] = int(fg_data.get("value", 50))
                data["fear_greed_classification"] = fg_data.get("value_classification", "Neutral")
            except:
                pass
        return data

    @staticmethod
    def fetch_asset_sentiment(exchange, symbol):
        """شاخص‌های مخصوص یک دارایی"""
        data = {"funding_rate": 0, "funding_interpretation": "neutral",
                "oi_delta_pct": 0, "oi_state": "stable",
                "price_change_pct": 0}
        if exchange is None:
            return data

        # Funding Rate
        try:
            funding = exchange.fetch_funding_rate(symbol)
            rate = funding.get("fundingRate", 0) * 100
            data["funding_rate"] = rate
            # تفسیر funding
            if rate > 0.2:
                data["funding_interpretation"] = "crowded long"
            elif rate > 0.05:
                data["funding_interpretation"] = "bullish"
            elif rate < -0.1:
                data["funding_interpretation"] = "crowded short"
            elif rate < -0.02:
                data["funding_interpretation"] = "bearish"
            else:
                data["funding_interpretation"] = "neutral"
        except:
            pass

        # Open Interest + Price Change
        try:
            oi_hist = exchange.fetch_open_interest_history(symbol, timeframe="1h", limit=2)
            if len(oi_hist) == 2:
                prev_oi = float(oi_hist[0]["openInterestAmount"])
                curr_oi = float(oi_hist[1]["openInterestAmount"])
                oi_change = ((curr_oi - prev_oi) / prev_oi) * 100 if prev_oi else 0
                data["oi_delta_pct"] = oi_change

                # دریافت قیمت متناظر (دو کندل آخر ۱ ساعته)
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1h", limit=2)
                if len(ohlcv) >= 2:
                    prev_close = float(ohlcv[-2][4])
                    curr_close = float(ohlcv[-1][4])
                    price_change = ((curr_close - prev_close) / prev_close) * 100 if prev_close else 0
                    data["price_change_pct"] = price_change

                    # تفسیر OI با قیمت
                    if oi_change > 0 and price_change > 0:
                        data["oi_state"] = "Long Build Up"
                    elif oi_change > 0 and price_change <= 0:
                        data["oi_state"] = "Short Build Up"
                    elif oi_change < 0 and price_change > 0:
                        data["oi_state"] = "Short Covering"
                    elif oi_change < 0 and price_change <= 0:
                        data["oi_state"] = "Long Unwinding"
        except:
            pass

        return data

    @staticmethod
    def fetch_sentiment(exchange, symbol=None):
        """ترکیب Global + Asset (برای سازگاری با کد قبلی)"""
        global_data = MarketSentiment.fetch_global_sentiment()
        asset_data = MarketSentiment.fetch_asset_sentiment(exchange, symbol) if symbol else {}
        return {**global_data, **asset_data}
