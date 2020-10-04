from entities.side import Side

class Transaction:
    def __init__(self, buyer_id: str, seller_id: str, maker_side: Side,
            instrument_id: int, price: int):
        self.buyer_id: str = buyer_id
        self.seller_id: str = seller_id
        self.maker_side: Side = maker_side
        self.instrument_id: int = instrument_id
        self.price: int = price
