from enum import IntEnum

class Side(IntEnum):
    BUY = 0
    SELL = 1

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

class Account:
    def __init__(self, discord_id, name, account_order, products):
        self.discord_id = discord_id
        self.name = name
        self.account_order = account_order

        self.balance = 0
        self.inventory = {product: 0 for product in products}
    
    def print_account(self):
        print(self.discord_id, self.name, self.balance, self.account_order)
        print(list(map(lambda x: (x[0].product_id, int(x[1])), self.inventory.items())))

class Transaction:
    def __init__(self, buyer_account, seller_account, product, price):
        self.buyer_account = buyer_account
        self.seller_account = seller_account
        self.price = price
        self.product = product
    def __str__(self):
        return self.seller_account.name + '->' + self.buyer_account.name + \
            ' for ' + str(self.product) + ' at ' + str(self.price)
