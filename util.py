from enum import IntEnum

class Side(IntEnum):
    BUY = 0
    SELL = 1

    def __str__(self):
        return str(self.name).lower()

class Product:
    def __init__(self, product_id, product_order, description):
        self.product_id = product_id
        self.product_order = product_order
        self.description = description

    def __str__(self):
        return "'" + self.description[:5] + "'"

class Order:
    def __init__(self, account, product, side, price):
        self.account = account
        self.product = product
        self.side = side
        self.price = price

class Transaction:
    def __init__(self, buyer_id, seller_id, is_buyer_maker, instrument_id, display_order, price):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.is_buyer_maker = is_buyer_maker
        self.instrument_id = instrument_id
        self.display_order = display_order
        self.price = price

    def __str__(self):
        return self.seller_id + '->' + self.buyer_id + \
            ' for ' + str(self.instrument_id) + ' at ' + str(self.price)
