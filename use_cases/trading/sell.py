from typing import Tuple

from entities.account import Account
from entities.instrument import Instrument
from entities.order import Order
from entities.order_status import OrderStatus
from entities.side import Side
from entities.transaction import Transaction

from use_cases.trading.common import BuySellUseCase

import settings

class SellUseCase(BuySellUseCase):
    def _is_sell_in_cross(self, account_id: str, instrument_id: int, sell_price: int) -> bool:
        existing_buy: Order = self.trading_repository.get_order(account_id, instrument_id, Side.BUY)
        return existing_buy is not None and sell_price <= existing_buy.price

    def sell(self, account_id: str, display_order: int, price: int) -> Tuple[int, dict]:
        seller_account: Account = self.account_repository.get_account_using_id(account_id)
        if seller_account is None:
            return (-1, None)

        instrument: Instrument = self.instrument_repository.get_instrument_using_display_order(display_order)
        if instrument is None:
            return (-2, None)
        
        if self._is_sell_in_cross(account_id, instrument.id, price):
            return (-3, None)
        
        if self.position_repository.get_account_position_in_instrument(seller_account, instrument) <= -settings.POSITION_LIMIT:
            return (-4, None)
        
        existing: Order = self.trading_repository.get_order(account_id, instrument.id, Side.SELL)
        if existing is not None:
            existing.status = OrderStatus.CANCELLED
            self.trading_repository.update_order_status_using_order(existing)
        
        sell_order: Order = Order(account_id, instrument.id, Side.SELL, price, OrderStatus.UNFILLED)
        try:
            best_buy: Order = self.trading_repository.get_best_buy_using_display_order(display_order, num_results = 1)[0]
        except IndexError:
            best_buy: Order = None

        if best_buy is None or best_buy.price < price:
            self.trading_repository.add_order(sell_order)
            return (0, None)
        
        best_buy.status = OrderStatus.FILLED
        sell_order.status = OrderStatus.FILLED
        self.trading_repository.update_order_status_using_order(best_buy)
        self.trading_repository.add_order(sell_order)

        buyer_account: Account = self.account_repository.get_account_using_id(best_buy.account_id)

        transaction: Transaction = Transaction(buyer_account, seller_account, Side.BUY, instrument, best_buy.price)
        self.process_transaction(transaction)

        return (0, transaction.to_dict())
