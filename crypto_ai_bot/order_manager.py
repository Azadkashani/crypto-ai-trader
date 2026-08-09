"""
Crypto AI Bot v1.2
Order Manager – Gate.io Testnet (official sandbox)
"""

import ccxt
from config import API_KEY, API_SECRET, TESTNET
from risk_manager import RiskManager

class OrderManager:
    def __init__(self):
        self.exchange = ccxt.gate({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'swap'},
        })
        if TESTNET:
            self.exchange.set_sandbox_mode(True)   # روش رسمی CCXT

    def set_leverage(self, symbol, leverage):
        try:
            self.exchange.set_leverage(leverage, symbol)
        except Exception as e:
            print(f"Error setting leverage: {e}")

    def place_market_order(self, symbol, side, quantity, stop_loss, take_profit, entry_price):
        dynamic_lev = RiskManager.suggest_leverage(entry_price, stop_loss, side, max_leverage=50)
        print(f"Using dynamic leverage: {dynamic_lev}x")
        self.set_leverage(symbol, dynamic_lev)

        order = self.exchange.create_order(
            symbol=symbol,
            type='market',
            side=side,
            amount=quantity,
        )
        sl_side = 'sell' if side == 'buy' else 'buy'
        tp_side = 'sell' if side == 'buy' else 'buy'

        sl_order = self.exchange.create_order(
            symbol=symbol,
            type='stop_market',
            side=sl_side,
            amount=quantity,
            params={'stopPrice': stop_loss}
        )
        tp_order = self.exchange.create_order(
            symbol=symbol,
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
            self.exchange.cancel_order(sl_order_id, symbol)
            positions = self.exchange.fetch_positions(symbols=[symbol])
            pos = next((p for p in positions if float(p.get('size', 0)) != 0), None)
            if not pos:
                return None
            sl_side = 'sell' if pos.get('side') == 'long' else 'buy'
            new_sl = self.exchange.create_order(
                symbol=symbol,
                type='stop_market',
                side=sl_side,
                amount=quantity,
                params={'stopPrice': new_stop_price}
            )
            return new_sl
        except Exception as e:
            print(f"Error modifying stop loss: {e}")
            return None

    def fetch_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            return balance['USDT']['free']
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0
