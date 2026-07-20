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

        macd = ta.trend.MACD(
            df["close"]
        )

        df["MACD"] = macd.macd()

        df["MACD_SIGNAL"] = macd.macd_signal()

        df["MACD_HIST"] = macd.macd_diff()



        # ==========================
        # ATR
        # ==========================

        df["ATR"] = ta.volatility.average_true_range(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=ATR_PERIOD
        )



        # ==========================
        # ADX Trend Strength
        # ==========================

        adx = ta.trend.ADXIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=14
        )


        df["ADX"] = adx.adx()

        df["+DI"] = adx.adx_pos()

        df["-DI"] = adx.adx_neg()



        # ==========================
        # Volume Analysis
        # ==========================

        df["AVG_VOLUME"] = (
            df["volume"]
            .rolling(20)
            .mean()
        )


        df["VOLUME_RATIO"] = (
            df["volume"] /
            df["AVG_VOLUME"]
        )



        # ==========================
        # Support Resistance
        # ==========================

        df["RESISTANCE_50"] = (
            df["high"]
            .rolling(50)
            .max()
        )


        df["SUPPORT_50"] = (
            df["low"]
            .rolling(50)
            .min()
        )



        # ==========================
        # Candle Momentum
        # ==========================

        df["BODY"] = (
            df["close"] -
            df["open"]
        )


        df["BODY_PERCENT"] = (
            abs(df["BODY"]) /
            df["open"]
        ) * 100



        # ==========================
        # Trend Direction
        # ==========================

        df["EMA_DISTANCE"] = (
            (df["EMA20"] - df["EMA50"])
            /
            df["EMA50"]
        ) * 100



        return df
