"""
Crypto AI Bot
News to Symbol Mapping
"""

SYMBOL_KEYWORDS = {
    "BTC": ["bitcoin", "btc", "satoshi", "xbt"],
    "ETH": ["ethereum", "eth", "vitalik", "ether"],
    "XRP": ["ripple", "xrp"],
    "SOL": ["solana", "sol"],
    "ADA": ["cardano", "ada"],
    "DOGE": ["dogecoin", "doge"],
    "BNB": ["binance coin", "bnb"],
    "UNI": ["uniswap", "uni"],
    "LTC": ["litecoin", "ltc"],
    "AAVE": ["aave"],
    "SHIB": ["shiba", "shib"],
    # ... (می‌توان گسترش داد)
}

class NewsMapping:
    @staticmethod
    def get_related_symbols(title):
        title_lower = title.lower()
        related = []
        for symbol, keywords in SYMBOL_KEYWORDS.items():
            if any(kw in title_lower for kw in keywords):
                related.append(symbol)
        # اگر هیچ ارز خاصی ذکر نشد، به کل بازار مربوط است
        if not related:
            related.append("MARKET")
        return related
