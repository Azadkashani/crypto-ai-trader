"""
Correlation Filter (BTC و ETH)
"""

import numpy as np

class CorrelationFilter:
    @staticmethod
    def detect(symbol, data_engine):
        try:
            btc_df = data_engine.get_ohlcv("BTC/USDT", timeframe="1h")
            if symbol == "BTC/USDT":
                return {"btc_correlation": 1.0}
            if btc_df is None or len(btc_df) < 20:
                return {"btc_correlation": None}
            df = data_engine.get_ohlcv(symbol, timeframe="1h")
            if df is None or len(df) < 20:
                return {"btc_correlation": None}
            btc_ret = btc_df["close"].pct_change().dropna()
            sym_ret = df["close"].pct_change().dropna()
            min_len = min(len(btc_ret), len(sym_ret))
            btc_ret = btc_ret.tail(min_len)
            sym_ret = sym_ret.tail(min_len)
            corr = np.corrcoef(btc_ret, sym_ret)[0, 1]
            return {"btc_correlation": round(corr, 4)}
        except:
            return {"btc_correlation": None}
