from typing import Tuple

from entities.account import Account
from entities.instrument import Instrument
from entities.order import Order
from entities.order_status import OrderStatus
from entities.side import Side
from entities.transaction import Transaction

from use_cases.trading.common import BuySellUseCase

import settings

class BuyUseCase(BuySellUseCase):
    def _is_buy_in_cross(self, account_id: str, instrument_id: int, buy_price: int) -> bool:
        existing_sell: Order = self.trading_repository.get_order(account_id, instrument_id, Side.SELL)
        return existing_sell is not None and existing_sell.price <= buy_price

    def buy(self, account_id: str, display_order: int, price: int) -> Tuple[int, dict]:
        buyer_account: Account = self.account_repository.get_account_using_id(account_id)
        if buyer_account is None:
            return (-1, None)
        
        instrument: Instrument = self.instrument_repository.get_instrument_using_display_order(display_order)
        if instrument is None:
            return (-2, None)
        
        if self._is_buy_in_cross(account_id, instrument.id, price):
            return (-3, None)
        
        if self.position_repository.get_account_position_in_instrument(buyer_account, instrument) >= settings.POSITION_LIMIT:
            return (-4, None)

        existing: Order = self.trading_repository.get_order(account_id, instrument.id, Side.BUY)
        if existing is not None:
            existing.status = OrderStatus.CANCELLED
            self.trading_repository.update_order_status_using_order(existing)

        buy_order: Order = Order(account_id, instrument.id, Side.BUY, price, OrderStatus.UNFILLED)
        try:
            best_sell: Order = self.trading_repository.get_best_sell_using_display_order(display_order, 1)[0]
        except IndexError:
            best_sell: Order = None

        if best_sell is None or price < best_sell.price:
            self.trading_repository.add_order(buy_order)
            return (0, None)
        
        buy_order.status = OrderStatus.FILLED
        best_sell.status = OrderStatus.FILLED
        self.trading_repository.add_order(buy_order)
        self.trading_repository.update_order_status_using_order(best_sell)
    
        seller_account: Account = self.account_repository.get_account_using_id(best_sell.account_id)

        transaction: Transaction = Transaction(buyer_account, seller_account, Side.SELL, instrument, best_sell.price)
        self.process_transaction(transaction)
    
        return (0, transaction.to_dict())
