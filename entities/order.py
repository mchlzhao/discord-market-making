from typing import Tuple

from entities.side import Side

class Order:
    def __init__(self, account_id: str, instrument_id: int, side: Side, price: int):
        self.account_id: str = account_id
        self.instrument_id: int = instrument_id
        self.side: Side = side
        self.price: int = price

    def __repr__(self):
        return ' '.join([self.account_id, str(self.instrument_id), str(self.side), str(self.price)])

    @classmethod
    def from_tuple(self, t: Tuple[str, int, str, int]):
        return Order(t[0], t[1], Side(t[2]), t[3])
