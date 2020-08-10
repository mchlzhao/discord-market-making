from util import Transaction, Side

class OrderBook:
    def __init__(self, product):
        self.product = product
        self.buy_orders = [list() for i in range(101)]
        self.sell_orders = [list() for i in range(101)]
    
    def test_if_match(self, price):
        if len(self.buy_orders[price]) == 0 or len(self.sell_orders[price]) == 0:
            return None
        return Transaction(self.buy_orders[price].pop(0), self.sell_orders[price].pop(0), self.product, price)
    
    def remove_account(self, account, side):
        if side == Side.BUY:
            for i in range(101):
                if account in self.buy_orders[i]:
                    self.buy_orders[i].remove(account)
                    return 0
        else:
            for i in range(101):
                if account in self.sell_orders[i]:
                    self.sell_orders[i].remove(account)
                    return 0
        return -1
    
    def add_order(self, account, side, price):
        if side == Side.BUY:
            self.buy_orders[price].append(account)
        else:
            self.sell_orders[price].append(account)
    
    def get_best_buy_price(self):
        for i in range(100, -1, -1):
            if len(self.buy_orders[i]) > 0:
                return i
        return -1
    
    def get_best_sell_price(self):
        for i in range(101):
            if len(self.sell_orders[i]) > 0:
                return i
        return 101
    
    def get_book_in_list(self, side):
        ret = []
        if side == Side.BUY:
            for i in range(100, -1, -1):
                ret.extend(map(lambda x: (x, i), self.buy_orders[i]))
        else:
            for i in range(101):
                ret.extend(map(lambda x: (x, i), self.sell_orders[i]))
        return ret
