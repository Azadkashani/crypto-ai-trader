"""
Crypto AI Bot
Order Manager – Binance Futures Testnet with Dynamic Leverage
"""

import ccxt
import time
from config import API_KEY, API_SECRET, TESTNET, TRAILING_STOP_ACTIVATION
from risk_manager import RiskManager


class OrderManager:
    def __init__(self):
        self.exchange = self._init_exchange()

    def _init_exchange(self):
        exchange = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'},
        })
        if TESTNET:
            exchange.urls['api'] = {
                'public': 'https://testnet.binancefuture.com/fapi/v1',
                'private': 'https://testnet.binancefuture.com/fapi/v1',
                'fapiPublic': 'https://testnet.binancefuture.com/fapi/v1',
                'fapiPrivate': 'https://testnet.binancefuture.com/fapi/v1',
            }
            exchange.set_sandbox_mode(True)
        return exchange

    def set_leverage(self, symbol, leverage):
        try:
            self.exchange.set_leverage(leverage, symbol.replace("/", ""))
        except Exception as e:
            print(f"Error setting leverage: {e}")

    def place_market_order(self, symbol, side, quantity, stop_loss, take_profit, entry_price):
        dynamic_lev = RiskManager.suggest_leverage(entry_price, stop_loss, side)
        print(f"Using dynamic leverage: {dynamic_lev}x")
        self.set_leverage(symbol, dynamic_lev)

        symbol_clean = symbol.replace("/", "")
        order = self.exchange.create_order(
            symbol=symbol_clean,
            type='market',
            side=side,
            amount=quantity,
        )
        print(f"Market order placed: {order['id']}")

        if side == 'buy':
            sl_side = 'sell'
            tp_side = 'sell'
        else:
            sl_side = 'buy'
            tp_side = 'buy'

        sl_order = self.exchange.create_order(
            symbol=symbol_clean,
            type='stop_market',
            side=sl_side,
            amount=quantity,
            params={'stopPrice': stop_loss}
        )
        tp_order = self.exchange.create_order(
            symbol=symbol_clean,
            type='limit',
            side=tp_side,
            amount=quantity,
            price=take_profit,
            params={'timeInForce': 'GTC'}
        )
        return {'entry_order': order, 'sl_order': sl_order, 'tp_order': tp_order}

    def check_open_positions(self, symbol=None):
        positions = self.exchange.fetch_positions(symbols=[symbol] if symbol else None)
        return [p for p in positions if float(p.get('size', 0)) != 0]

    def modify_stop_loss(self, symbol, sl_order_id, new_stop_price, quantity):
        try:
            self.exchange.cancel_order(sl_order_id, symbol.replace("/", ""))
            sl_order = self.exchange.create_order(
                symbol=symbol.replace("/", ""),
                type='stop_market',
                side='sell',
                amount=quantity,
                params={'stopPrice': new_stop_price}
            )
            return sl_order
        except Exception as e:
            print(f"Error modifying stop loss: {e}")
            return None

    def fetch_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            return balance['USDT']['free']
        except:
            return 0
