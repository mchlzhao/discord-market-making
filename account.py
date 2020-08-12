from util import Side

class Account:
    def __init__(self, account_id, name, account_order, products):
        self.account_id = account_id
        self.name = name
        self.account_order = account_order
        self.products = products

        self.balance = 0
        self.inventory = {product: 0 for product in self.products}
    
    def print_account(self):
        print(self.account_id, self.name, self.balance, self.account_order)
        print(list(map(lambda x: (x[0].product_id, int(x[1])), self.inventory.items())))

    def process_transaction(self, product, side, price):
        if side == Side.BUY:
            self.balance -= price
            self.inventory[product] += 1
        else:
            self.balance += price
            self.inventory[product] -= 1