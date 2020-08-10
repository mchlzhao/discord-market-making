from util import Transaction, Side

class OrderBook:
    def __init__(self, product):
        self.product = product
        self.buy_orders = [list() for i in range(101)]
        self.sell_orders = [list() for i in range(101)]
    
    def add_order(self, account, side, price):
        if side == Side.BUY:
            self.buy_orders[price].append(account)
        else:
            self.sell_orders[price].append(account)
    
    def remove_order(self, account, side, price):
        if side == Side.BUY:
            self.buy_orders[price].remove(account)
        else:
            self.sell_orders[price].remove(account)
    
    def get_best_buy(self):
        for i in range(100, -1, -1):
            if len(self.buy_orders[i]) > 0:
                return (self.buy_orders[i][0], i)
        return None
    
    def get_best_sell(self):
        for i in range(101):
            if len(self.sell_orders[i]) > 0:
                return (self.sell_orders[i][0], i)
        return None
    
    def get_book_in_list(self, side):
        ret = []
        if side == Side.BUY:
            for i in range(100, -1, -1):
                ret.extend(map(lambda x: (x, i), self.buy_orders[i]))
        else:
            for i in range(101):
                ret.extend(map(lambda x: (x, i), self.sell_orders[i]))
        return ret
