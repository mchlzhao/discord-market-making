from typing import List, Tuple

from entities.instrument import Instrument
from entities.order import Order
from entities.side import Side

class ITradingRepository:
    def add_order(self, order: Order, status: str) -> None:
        raise NotImplementedError()

    def get_best_buy_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def get_best_buy_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def get_best_sell_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def get_best_sell_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def update_order_status(self, order: Order, status: str) -> None:
        raise NotImplementedError()

    def update_order_status_using(self, account_id: str, display_order: int, side: Side, status: str) -> None:
        raise NotImplementedError()

    def get_existing_order(self, account_id: str, display_order: int, side: Side) -> Tuple:
        raise NotImplementedError()
