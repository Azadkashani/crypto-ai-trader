"""
Crypto AI Bot v5.7
Market Data Engine
"""

import ccxt
import pandas as pd

from config import EXCHANGE_NAME
from config import TIMEFRAME
from config import LIMIT


class MarketData:


    def __init__(self):

        if EXCHANGE_NAME.lower() == "gate":

            self.exchange = ccxt.gate({
                "enableRateLimit": True
            })

        else:

            raise Exception(
                "Exchange Not Supported"
            )



    # =====================================
    # Single Timeframe Data
    # =====================================

    def get_ohlcv(
            self,
            symbol,
            timeframe=None
    ):


        if timeframe is None:

            timeframe = TIMEFRAME



        candles = self.exchange.fetch_ohlcv(

            symbol,

            timeframe=timeframe,

            limit=LIMIT

        )



        df = pd.DataFrame(

            candles,

            columns=[

                "time",

                "open",

                "high",

                "low",

                "close",

                "volume"

            ]

        )



        df["time"] = pd.to_datetime(

            df["time"],

            unit="ms"

        )


        return df



    # =====================================
    # Multi Timeframe Data
    # =====================================

    def get_multi_timeframe(

            self,

            symbol,

            timeframes

    ):


        data = {}



        for tf in timeframes:


            try:

                data[tf] = self.get_ohlcv(

                    symbol,

                    tf

                )


            except Exception as e:

                print(

                    f"{symbol} {tf}: {e}"

                )



        return data




    # =====================================
    # USDT Markets
    # =====================================

    def get_usdt_symbols(self):


        markets = self.exchange.load_markets()


        symbols = []



        for symbol, market in markets.items():


            if (

                market.get("active", False)

                and market.get("spot", False)

                and market.get("quote") == "USDT"

            ):

                symbols.append(symbol)



        symbols.sort()


        return symbols
