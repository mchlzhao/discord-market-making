from entities.account import Account
from entities.instrument import Instrument
from entities.side import Side

class Order:
    def __init__(self, account: Account, instrument: Instrument, side: Side, price: int):
        self.account: Account = account
        self.instrument: Instrument = instrument
        self.side: Side = side
        self.price: int = price

    def __repr__(self):
        return ' '.join([self.account.name, self.instrument.id, str(self.side), str(self.price)])