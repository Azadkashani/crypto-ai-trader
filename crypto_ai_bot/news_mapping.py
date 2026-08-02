"""
Crypto AI Bot v1.1
News to Symbol Mapping with BTC multiplier
"""

SYMBOL_KEYWORDS = {
    "BTC": ["bitcoin", "btc", "xbt"],
    "ETH": ["ethereum", "eth", "ether"],
    "XRP": ["ripple", "xrp"],
    "SOL": ["solana", "sol"],
    "ADA": ["cardano", "ada"],
    "DOGE": ["dogecoin", "doge"],
    "BNB": ["binance coin", "bnb"],
    "UNI": ["uniswap", "uni"],
    "LTC": ["litecoin", "ltc"],
    "AAVE": ["aave"],
    "SHIB": ["shiba", "shib"],
    # سایر نمادها در صورت نیاز اضافه شوند
}

class NewsMapping:
    @staticmethod
    def get_related_symbols(title):
        title_lower = title.lower()
        related = []
        for symbol, keywords in SYMBOL_KEYWORDS.items():
            if any(kw in title_lower for kw in keywords):
                related.append(symbol)
        if not related:
            related.append("MARKET")
        # اگر BTC در میان نمادها بود و نمادهای دیگری هم وجود دارند،
        # تأثیر BTC روی آلت‌کوین‌ها با ضریب 0.5 اعمال خواهد شد (در NewsScoring)
        return related
