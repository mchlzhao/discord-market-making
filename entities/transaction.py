from entities.account import Account
from entities.instrument import Instrument
from entities.side import Side

class Transaction:
    def __init__(self, buyer_account: Account, seller_account: Account, maker_side: Side,
            instrument: Instrument, price: int):
        self.buyer_account: Account = buyer_account
        self.seller_account: Account = seller_account
        self.maker_side: Side = maker_side
        self.instrument: Instrument = instrument
        self.price: int = price
