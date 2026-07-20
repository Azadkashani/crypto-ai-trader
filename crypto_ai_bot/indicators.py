"""
Crypto AI Bot v5.2
Indicator Engine
"""

import ta

from config import (
    EMA_FAST,
    EMA_MID,
    EMA_SLOW,
    RSI_PERIOD,
    ATR_PERIOD
)


class IndicatorEngine:

    @staticmethod
    def calculate(df):

        # ==========================
        # EMA
        # ==========================

        df["EMA20"] = ta.trend.ema_indicator(
            df["close"],
            window=EMA_FAST
        )

        df["EMA50"] = ta.trend.ema_indicator(
            df["close"],
            window=EMA_MID
        )

        df["EMA200"] = ta.trend.ema_indicator(
            df["close"],
            window=EMA_SLOW
        )


        # ==========================
        # RSI
        # ==========================

        df["RSI"] = ta.momentum.rsi(
            df["close"],
            window=RSI_PERIOD
        )


        # ==========================
        # MACD
        # ==========================

        df["MACD"] = ta.trend.macd(
            df["close"]
        )

        df["MACD_SIGNAL"] = ta.trend.macd_signal(
            df["close"]
        )


        # ==========================
        # ATR
        # ==========================

        df["ATR"] = ta.volatility.average_true_range(
            df["high"],
            df["low"],
            df["close"],
            window=ATR_PERIOD
        )


        # ==========================
        # ADX Trend Strength
        # ==========================

        adx_indicator = ta.trend.ADXIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=14
        )

        df["ADX"] = adx_indicator.adx()

        df["+DI"] = adx_indicator.adx_pos()

        df["-DI"] = adx_indicator.adx_neg()


        # ==========================
        # Volume Average
        # ==========================

        df["AVG_VOLUME"] = (
            df["volume"]
            .rolling(20)
            .mean()
        )


        return df
