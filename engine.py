from util import Side, Transaction
from order_book import OrderBook

import settings

class Engine:
    def __init__(self, accounts, products):
        self.accounts = accounts
        self.products = products

        self.order_books = {product: OrderBook(product) for product in products}
        self.orders_by_account = {} # key = (account, product, side)

        self.transaction_history = []
    
    def account_has_existing_order(self, account, product, side):
        if (account, product, side) not in self.orders_by_account:
            return -1
        return self.orders_by_account[(account, product, side)]

    # now it is assumed that the bid placed is a valid bid
    # position limit and in cross with self are checked before calling process_bid()
    # process_bid() will do automatic rounding to the best opposing bid
    def process_bid(self, account, product, side, price):
        order_book = self.order_books[product]

        existing = self.account_has_existing_order(account, product, side)
        if existing != -1:
            self.process_cancel(account, product, side)

        if side == Side.BUY:
            lowest_sell = order_book.get_best_sell()

            if lowest_sell == None or price < lowest_sell[1]:
                # no trade is made
                order_book.add_order(account, side, price)
                self.orders_by_account[(account, product, side)] = price

                return None
            
            transaction = Transaction(account, lowest_sell[0], product, lowest_sell[1])
            self.process_cancel(lowest_sell[0], product, Side.SELL)
        else:
            highest_buy = order_book.get_best_buy()

            if highest_buy == None or price > highest_buy[1]:
                # no trade is made
                order_book.add_order(account, side, price)
                self.orders_by_account[(account, product, side)] = price

                return None
            
            transaction = Transaction(highest_buy[0], account, product, highest_buy[1])
            self.process_cancel(highest_buy[0], product, Side.BUY)
        
        self.transaction_history.append(transaction)

        return transaction
    
    # return -1: no existing order to cancel
    # assumed the order does exist
    def process_cancel(self, account, product, side):
        order_book = self.order_books[product]
        order_book.remove_order(account, side, self.orders_by_account[(account, product, side)])
        self.orders_by_account.pop((account, product, side))
    
    def print_order_books(self):
        for product, book in self.order_books.items():
            print(product.description)
            print(list(map(lambda x: (x[0].name, x[1]), book.get_book_in_list(Side.BUY))))
            print(list(map(lambda x: (x[0].name, x[1]), book.get_book_in_list(Side.SELL))))
            print()
        
        for key, value in self.orders_by_account.items():
            print(key[0].name, key[1].product_id, int(key[2]), value)