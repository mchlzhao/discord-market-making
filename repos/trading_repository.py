from typing import List

from entities.order import Order
from entities.side import Side

class ITradingRepository:
    def add_order(self, order: Order) -> None:
        raise NotImplementedError()

    def update_order_status_using_order(self, order: Order) -> None:
        raise NotImplementedError()

    def get_order(self, account_id: str, instrument_id: int, side: Side) -> Order:
        raise NotImplementedError()

    def get_best_buy_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def get_best_buy_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def get_best_sell_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def get_best_sell_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        raise NotImplementedError()

    def cancel_orders_using_display_order(self, display_order: int) -> None:
        raise NotImplementedError()
