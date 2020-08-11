import settings

class Account:
    def __init__(self, discord_id, name, account_order):
        self.discord_id = discord_id
        self.name = name
        self.account_order = account_order

        self.balance = 0
        self.inventory = {product: 0 for product in settings.PRODUCTS}
    
    def print_account(self):
        print(self.discord_id, self.name, self.balance, self.account_order)
        print(list(map(lambda x: (x[0].product_id, int(x[1])), self.inventory.items())))
