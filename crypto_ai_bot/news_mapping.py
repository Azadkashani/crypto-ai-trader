"""
Crypto AI Bot v1.1
News to Symbol Mapping (with word boundaries)
"""

import re

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
    "PEPE": ["pepe"],
    "LINK": ["chainlink", "link"],
    "MATIC": ["polygon", "matic"],
    "DOT": ["polkadot", "dot"],
    "AVAX": ["avalanche", "avax"],
    "ATOM": ["cosmos", "atom"],
    "FIL": ["filecoin", "fil"],
    "APT": ["aptos", "apt"],
    "ARB": ["arbitrum", "arb"],
    "OP": ["optimism", "op"],
    "NEAR": ["near protocol", "near"],
    "INJ": ["injective", "inj"],
    "TIA": ["celestia", "tia"],
    "SUI": ["sui"],
    "SEI": ["sei"],
}

class NewsMapping:
    @staticmethod
    def get_related_symbols(title):
        title_lower = title.lower()
        related = []
        for symbol, keywords in SYMBOL_KEYWORDS.items():
            for kw in keywords:
                # تطبیق فقط در صورت کلمهٔ کامل (با مرز)
                if re.search(r'\b' + re.escape(kw) + r'\b', title_lower):
                    related.append(symbol)
                    break   # هر نماد را یک‌بار اضافه کن
        if not related:
            related.append("MARKET")
        return related
