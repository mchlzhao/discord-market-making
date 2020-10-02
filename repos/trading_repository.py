from typing import List, Tuple

from entities.instrument import Instrument
from entities.order import Order
from entities.side import Side
from entities.transaction import Transaction

class TradingRepository:
    def add_order(self, order: Order, status: str) -> None:
        raise NotImplementedError()

    def get_best_buy(self, instrument: Instrument, num_results: int = None) -> List[Tuple]:
        raise NotImplementedError()

    def get_best_sell(self, instrument: Instrument, num_results: int = None) -> List[Tuple]:
        raise NotImplementedError()

    def update_order_status(self, order: Order, status: str) -> None:
        raise NotImplementedError()

    def update_order_status_using_order_id(self, order_id: int, status: str) -> None:
        raise NotImplementedError()

    def get_existing_order(self, account_id: str, display_order: int, side: Side) -> Tuple:
        raise NotImplementedError()

    def add_transaction(self, transaction: Transaction) -> None:
        raise NotImplementedError()
