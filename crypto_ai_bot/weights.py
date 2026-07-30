"""
Crypto AI Bot
Analysis Weights System
"""

REASON_WEIGHTS = {
    # ★★★★★ (حیاتی)
    "Market Structure Bullish": 5,
    "Market Structure Bearish": 5,
    "BOS Bullish Break": 5,
    "BOS Bearish Break": 5,
    "Strong ADX": 4,
    "Bullish MACD": 4,
    "MTF Strong Bullish": 5,
    "MTF Strong Bearish": 5,
    "Real Breakout": 5,
    "Trending Market": 4,
    # ★★★★ (بسیار مهم)
    "EMA20 > EMA50": 4,
    "EMA50 > EMA200": 4,
    "+DI > -DI": 3,
    "Healthy RSI": 3,
    "High Volume": 4,
    "Bullish Order Block": 4,
    "RSI Bullish Divergence": 4,
    "MACD Bullish Divergence": 4,
    # ★★★ (مهم)
    "MTF Bullish": 3,
    "Volume Breakout": 3,
    "Price Above VWAP": 3,
    "Discount Zone": 3,
    "Buy Side Liquidity Sweep": 3,
    "Bullish Trendline Break": 3,
    "Strong Support": 3,
    "OI Long Build Up": 3,
    "Funding Bullish Bias": 2,
    # ★★ (کمکی)
    "Unfilled Bullish FVG": 2,
    "Near POC": 2,
    "EMA Slopes Positive": 2,
    "Bullish Candlestick": 2,
    "Price in Golden Zone": 2,
    "London Session": 1,
    "New York Session": 1,
    "Low Volatility Contraction": 2,
    "High BTC Correlation": 2,
    "OI Short Covering": 2,
}

WARNING_WEIGHTS = {
    # ★★★★★ (بحرانی)
    "Market Structure Bearish": 5,
    "BOS Bearish Break": 5,
    "Opposing CHoCH (active)": 5,
    "MTF Strong Bearish": 5,
    "Bearish DI": 4,
    "Fake Breakout": 5,
    "Bearish Trendline Break": 4,
    # ★★★★ (جدی)
    "Bearish Order Block": 4,
    "RSI Bearish Divergence": 4,
    "MACD Bearish Divergence": 4,
    "Bearish Candlestick": 3,
    "OI Short Build Up": 3,
    "Strong Resistance": 3,
    "Price Near Resistance": 4,
    "High Volatility": 3,
    # ★★★ (متوسط)
    "Low Volume": 3,
    "MTF Bearish": 3,
    "Price Below VWAP": 3,
    "Premium Zone": 2,
    "Sell Side Liquidity Sweep": 3,
    "Unfilled Bearish FVG": 2,
    "OI Long Unwinding": 2,
    "Ranging/Choppy": 3,
    # ★★ (خفیف)
    "Funding Bearish Bias": 2,
    "Sideways Trend": 2,
    "Bearish Trend": 5,
}
