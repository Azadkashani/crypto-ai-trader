"""
Crypto AI Bot
Order Manager – Gate.io Testnet Futures with Dynamic Leverage
"""

import ccxt
import time
from config import API_KEY, API_SECRET, TESTNET, TRAILING_STOP_ACTIVATION
from risk_manager import RiskManager


class OrderManager:
    def __init__(self):
        self.exchange = self._init_exchange()
        self.open_orders = []

    def _init_exchange(self):
        exchange = ccxt.gate({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'swap'},
        })
        if TESTNET:
            exchange.urls['api'] = {
                'public': 'https://fx-api-testnet.gateio.ws/api/v4',
                'private': 'https://fx-api-testnet.gateio.ws/api/v4',
            }
        return exchange

    def set_leverage(self, symbol, leverage):
        try:
            self.exchange.set_leverage(leverage, symbol)
        except Exception as e:
            print(f"Error setting leverage: {e}")

    def place_market_order(self, symbol, side, quantity, stop_loss, take_profit, entry_price):
        """
        ارسال سفارش مارکت با اهرم پویا
        """
        # محاسبه اهرم پویا
        dynamic_lev = RiskManager.suggest_leverage(entry_price, stop_loss, side)
        print(f"Using dynamic leverage: {dynamic_lev}x")
        self.set_leverage(symbol, dynamic_lev)

        # سفارش اصلی
        order = self.exchange.create_order(
            symbol=symbol,
            type='market',
            side=side,
            amount=quantity,
        )
        print(f"Market order placed: {order['id']}")

        # حد ضرر و سود
        if side == 'buy':
            sl_side = 'sell'
            tp_side = 'sell'
            sl_price = stop_loss
            tp_price = take_profit
        else:
            sl_side = 'buy'
            tp_side = 'buy'
            sl_price = stop_loss
            tp_price = take_profit

        # Stop Loss
        sl_order = self.exchange.create_order(
            symbol=symbol,
            type='stop_market',
            side=sl_side,
            amount=quantity,
            params={'stopPrice': sl_price}
        )
        # Take Profit
        tp_order = self.exchange.create_order(
            symbol=symbol,
            type='limit',
            side=tp_side,
            amount=quantity,
            price=tp_price,
            params={'timeInForce': 'GTC'}
        )
        return {
            'entry_order': order,
            'sl_order': sl_order,
            'tp_order': tp_order
        }

    def check_open_positions(self, symbol=None):
        positions = self.exchange.fetch_positions(symbols=[symbol] if symbol else None)
        return [p for p in positions if float(p.get('size', 0)) != 0]

    def modify_stop_loss(self, symbol, sl_order_id, new_stop_price, quantity):
        try:
            self.exchange.cancel_order(sl_order_id, symbol)
            sl_side = 'sell'  # برای لانگ (می‌توان داینامیک کرد)
            sl_order = self.exchange.create_order(
                symbol=symbol,
                type='stop_market',
                side=sl_side,
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
