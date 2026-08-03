"""
Crypto AI Bot
Advanced Analytics Aggregator
"""

from config import (
    ENABLE_LIQUIDITY_SWEEP,
    ENABLE_FVG,
    ENABLE_ORDER_BLOCK,
    ENABLE_PREMIUM_DISCOUNT,
    ENABLE_VOLUME_PROFILE,
    ENABLE_VWAP,
    ENABLE_OPEN_INTEREST,
    ENABLE_FUNDING_RATE,
    ENABLE_ATR_VOLATILITY,
    ENABLE_EMA_SLOPE,
    ENABLE_RSI_DIVERGENCE,
    ENABLE_MACD_DIVERGENCE,
    ENABLE_CANDLESTICK_PATTERNS,
    ENABLE_SR_STRENGTH,
    ENABLE_BREAKOUT_QUALITY,
    ENABLE_TRENDLINE_BREAK,
    ENABLE_FIBONACCI,
    ENABLE_SESSION_DETECTION,
    ENABLE_MARKET_REGIME,
    ENABLE_CORRELATION_FILTER,
)

from liquidity_sweep import LiquiditySweep
from fvg import FVG
from order_block import OrderBlock
from premium_discount import PremiumDiscount
from volume_profile import VolumeProfile
from vwap import VWAP
from open_interest import OpenInterest
from funding_rate import FundingRate
from atr_volatility import ATRVolatility
from ema_slope import EMASlope
from rsi_divergence import RSIDivergence
from macd_divergence import MACDDivergence
from candlestick_patterns import CandlestickPatterns
from sr_strength import SRStrength
from breakout_quality import BreakoutQuality
from trendline_break import TrendlineBreak
from fibonacci import Fibonacci
from session_detection import SessionDetection
from market_regime import MarketRegime
from correlation_filter import CorrelationFilter


class AdvancedAnalytics:
    def __init__(self, data_engine=None):
        self.data_engine = data_engine

    def analyze(self, df, market_structure=None, symbol=None):
        result = {}

        if ENABLE_LIQUIDITY_SWEEP:
            result["liquidity_sweep"] = LiquiditySweep.detect(df, market_structure)
        if ENABLE_FVG:
            result["fvg"] = FVG.detect(df)
        if ENABLE_ORDER_BLOCK:
            result["order_block"] = OrderBlock.detect(df, market_structure)
        if ENABLE_PREMIUM_DISCOUNT:
            result["premium_discount"] = PremiumDiscount.detect(df, market_structure)
        if ENABLE_VOLUME_PROFILE:
            result["volume_profile"] = VolumeProfile.detect(df)
        if ENABLE_VWAP:
            result["vwap"] = VWAP.detect(df)
        if ENABLE_OPEN_INTEREST and self.data_engine:
            result["open_interest"] = OpenInterest.detect(symbol, self.data_engine.exchange, df)
        if ENABLE_FUNDING_RATE and self.data_engine:
            result["funding_rate"] = FundingRate.detect(symbol, self.data_engine.exchange)
        if ENABLE_ATR_VOLATILITY:
            result["atr_volatility"] = ATRVolatility.detect(df)
        if ENABLE_EMA_SLOPE:
            result["ema_slope"] = EMASlope.detect(df)
        if ENABLE_RSI_DIVERGENCE:
            result["rsi_divergence"] = RSIDivergence.detect(df)
        if ENABLE_MACD_DIVERGENCE:
            result["macd_divergence"] = MACDDivergence.detect(df)
        if ENABLE_CANDLESTICK_PATTERNS:
            result["candlestick_patterns"] = CandlestickPatterns.detect(df)
        if ENABLE_SR_STRENGTH:
            result["sr_strength"] = SRStrength.detect(df)
        if ENABLE_BREAKOUT_QUALITY:
            result["breakout_quality"] = BreakoutQuality.detect(df)
        if ENABLE_TRENDLINE_BREAK:
            result["trendline_break"] = TrendlineBreak.detect(df)
        if ENABLE_FIBONACCI:
            result["fibonacci"] = Fibonacci.detect(df, market_structure)
        if ENABLE_SESSION_DETECTION:
            result["session"] = SessionDetection.detect()
        if ENABLE_MARKET_REGIME:
            result["market_regime"] = MarketRegime.detect(df)
        if ENABLE_CORRELATION_FILTER and self.data_engine:
            result["correlation"] = CorrelationFilter.detect(symbol, self.data_engine)

        return result
