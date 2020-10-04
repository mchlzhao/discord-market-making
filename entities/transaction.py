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

    def to_dict(self):
        return {
            'buyer_id': self.buyer_account.id,
            'seller_id': self.seller_account.id,
            'is_buyer_maker': self.maker_side == Side.BUY,
            'display_order': self.instrument.display_order,
            'price': self.price
        }
