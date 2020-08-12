from util import Side, Transaction

class OrderBook:
    def __init__(self, product):
        '''
        order book stores the accounts of bidders in the index of the price they bid at
        at each index, accounts are stored in a list ordered by earliest bid first
        '''
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
        '''
        returns (Account, price) of the highest priced buyer, breaking ties by earliest bid
        '''
        for i in range(100, -1, -1):
            if len(self.buy_orders[i]) > 0:
                return (self.buy_orders[i][0], i)
        return None
    
    def get_best_sell(self):
        '''
        returns (Account, price) of the lowest priced seller, breaking ties by earliest bid
        '''
        for i in range(101):
            if len(self.sell_orders[i]) > 0:
                return (self.sell_orders[i][0], i)
        return None
    
    def get_book_in_list(self, side):
        '''
        flattens order book into 1D list
        orders the return list by price-time priority, with highest priority first
        '''
        ret = []
        if side == Side.BUY:
            for i in range(100, -1, -1):
                ret.extend(map(lambda x: (x, i), self.buy_orders[i]))
        else:
            for i in range(101):
                ret.extend(map(lambda x: (x, i), self.sell_orders[i]))
        return ret
