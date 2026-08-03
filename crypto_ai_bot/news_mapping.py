"""
Crypto AI Bot v1.2
News to Symbol Mapping – Multi-level asset detection with weights and confidence
"""

import re

# نگاشت دارایی‌ها به کلمات کلیدی (دارایی‌های اصلی)
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

# نگاشت دارایی‌های مرتبط با اکوسیستم (Ecosystem mapping)
ECOSYSTEM_MAP = {
    "ETH": ["ARB", "OP", "LDO", "MATIC", "UNI", "LINK", "AAVE", "CRV", "SNX", "COMP", "MKR"],
    "SOL": ["BONK", "JTO", "PYTH", "JUP"],
    "AVAX": ["JOE", "QI"],
    "DOT": ["KSM", "GLMR", "ACA"],
    "ATOM": ["OSMO", "JUNO", "EVMOS"],
    "NEAR": ["AURORA", "REF"],
    "BTC": ["STX", "RIF"],
    "BNB": ["CAKE", "XVS", "BAKE"],
}

class NewsMapping:
    # کلمات کلیدی کل بازار
    MARKET_KEYWORDS = [
        "fed", "fomc", "interest rate", "cpi", "gdp", "inflation",
        "war", "ban", "regulation", "sec", "cftc", "congress",
        "macro", "recession", "stimulus", "qe", "taper"
    ]

    @staticmethod
    def get_related_assets(title):
        title_lower = title.lower()
        assets = []
        # تشخیص دارایی‌های خاص
        for symbol, keywords in SYMBOL_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', title_lower):
                    assets.append({"symbol": symbol, "weight": 1.0, "type": "specific", "confidence": 0.95})
                    break

        # تشخیص اکوسیستم: اگر یک دارایی خاص داریم، دارایی‌های مرتبط را با وزن کمتر اضافه کن
        for asset in assets[:]:  # تکرار روی یک کپی
            if asset["symbol"] in ECOSYSTEM_MAP:
                for eco_symbol in ECOSYSTEM_MAP[asset["symbol"]]:
                    # اگر قبلاً اضافه نشده باشد
                    if not any(a["symbol"] == eco_symbol for a in assets):
                        assets.append({"symbol": eco_symbol, "weight": 0.3, "type": "ecosystem", "confidence": 0.6})

        # تشخیص کل بازار (با وزن کم)
        is_market = any(re.search(r'\b' + kw + r'\b', title_lower) for kw in NewsMapping.MARKET_KEYWORDS)
        if is_market:
            # اگر قبلاً market اضافه نشده
            if not any(a["symbol"] == "MARKET" for a in assets):
                assets.append({"symbol": "MARKET", "weight": 0.5, "type": "market", "confidence": 0.8})

        # اگر هیچ دارایی شناسایی نشد و خبر کل بازار هم نبود، خالی برگردان (دیگر MARKET پیش‌فرض نیست)
        if not assets:
            return []

        # مرتب‌سازی بر اساس weight نزولی
        assets.sort(key=lambda x: x["weight"], reverse=True)
        return assets
