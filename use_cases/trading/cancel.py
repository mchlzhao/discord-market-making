from entities.account import Account
from entities.instrument import Instrument
from entities.order import Order
from entities.order_status import OrderStatus
from entities.side import Side

from use_cases.trading.common import TradingUseCase

class CancelUseCase(TradingUseCase):
    def _cancel(self, account_id: str, display_order: int, side: Side) -> int:
        account: Account = self.account_repository.get_account_using_id(account_id)
        if account is None:
            return -1
        
        instrument: Instrument = self.instrument_repository.get_instrument_using_display_order(display_order)
        if instrument is None:
            return -2

        order: Order = self.trading_repository.get_order(account_id, instrument.id, side)
        if order is None:
            return -3

        order.status = OrderStatus.CANCELLED
        self.trading_repository.update_order_status_using_order(order)

        return 0

    def cancel_buy(self, account_id: str, display_order: int) -> int:
        return self._cancel(account_id, display_order, Side.BUY)

    def cancel_sell(self, account_id: str, display_order: int) -> int:
        return self._cancel(account_id, display_order, Side.SELL)
