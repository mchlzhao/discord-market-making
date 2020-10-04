from typing import Tuple

from entities.order_status import OrderStatus
from entities.side import Side

class Order:
    def __init__(self, account_id: str, instrument_id: int, side: Side, price: int, status: OrderStatus):
        self.account_id: str = account_id
        self.instrument_id: int = instrument_id
        self.side: Side = side
        self.price: int = price
        self.status: OrderStatus = status

    def __repr__(self):
        return 'Order: ' + ' '.join([
            self.account_id,
            str(self.instrument_id),
            str(self.side),
            str(self.price),
            str(self.status)
        ])

    @classmethod
    def from_tuple(cls, t: Tuple[str, int, str, int, str]):
        return cls(t[0], t[1], Side(t[2]), t[3], OrderStatus(t[4]))
