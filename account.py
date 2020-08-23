from util import Side

class Account:
    def __init__(self, id, name, account_order, products):
        self.id = id
        self.name = name
        self.account_order = account_order
        self.products = products

        self.balance = 0
        self.inventory = {product: 0 for product in self.products}
        self.total_positions = 0
    
    def print_account(self):
        '''
        for debugging purposes
        prints account info and its positions in each product
        '''
        print(self.id, self.name, self.balance, self.account_order)
        print(list(map(lambda x: (x[0].product_id, int(x[1])), self.inventory.items())))
    
    def add_inventory(self, product, change):
        self.total_positions -= abs(self.inventory[product])
        self.inventory[product] += change
        self.total_positions += abs(self.inventory[product])

    def process_transaction(self, product, side, price):
        if side == Side.BUY:
            self.balance -= price
            self.add_inventory(product, 1)
        else:
            self.balance += price
            self.add_inventory(product, -1)