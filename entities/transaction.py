from entities.account import Account
from entities.instrument import Instrument

class Transaction:
    def __init__(self, buyer_account: Account, seller_account: Account, is_buyer_maker: bool,
            instrument: Instrument, price: int):
        self.buyer_account: Account = buyer_account
        self.seller_account: Account = seller_account
        self.is_buyer_maker: bool = is_buyer_maker
        self.instrument: Instrument = instrument
        self.price: int = price
