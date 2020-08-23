from util import Side, Transaction
from order_book import OrderBook

class Engine:
    def __init__(self, accounts, products):
        self.accounts = accounts
        self.products = products

        self.order_books = {product: OrderBook(product) for product in products}
        self.orders_dict = {} # key = (account, product, side), value = price

        self.transaction_history = []
    
    def account_has_existing_order(self, account, product, side):
        if (account, product, side) not in self.orders_dict:
            return -1
        return self.orders_dict[(account, product, side)]

    def process_bid(self, account, product, side, price):
        '''
        process a bid
        assumes the bid is valid, as all error checks are performed by controller

        if a trade is made:
            opposite side will be removed from the engine
            returns Transaction object
        else:
            bid is entered into the order book
            returns None
        '''
        order_book = self.order_books[product]

        existing = self.account_has_existing_order(account, product, side)
        if existing != -1:
            self.process_cancel(account, product, side)

        if side == Side.BUY:
            lowest_sell = order_book.get_best_sell()
            if lowest_sell == None or price < lowest_sell[1]:
                order_book.add_order(account, side, price)
                self.orders_dict[(account, product, side)] = price

                return None
            
            transaction = Transaction(account, lowest_sell[0], product, lowest_sell[1])
            self.process_cancel(lowest_sell[0], product, Side.SELL)

        else:
            highest_buy = order_book.get_best_buy()
            if highest_buy == None or price > highest_buy[1]:
                order_book.add_order(account, side, price)
                self.orders_dict[(account, product, side)] = price

                return None
            
            transaction = Transaction(highest_buy[0], account, product, highest_buy[1])
            self.process_cancel(highest_buy[0], product, Side.BUY)
        
        self.transaction_history.append(transaction)

        return transaction
    
    def process_cancel(self, account, product, side):
        '''
        process a cancellation
        assumes the operation is valid as error checks are performed by controller
        '''
        order_book = self.order_books[product]
        order_book.remove_order(account, side, self.orders_dict[(account, product, side)])
        self.orders_dict.pop((account, product, side))
    
    def print_order_books(self):
        '''
        for debugging purposes
        prints state of the order books for all products
        '''
        for product, book in self.order_books.items():
            print(product.description)
            print(list(map(lambda x: (x[0].name, x[1]), book.get_book_in_list(Side.BUY))))
            print(list(map(lambda x: (x[0].name, x[1]), book.get_book_in_list(Side.SELL))))
            print()
        
        for key, value in self.orders_dict.items():
            print(key[0].name, key[1].product_id, int(key[2]), value)
    
    def clear_orders(self):
        '''
        removes all orders from all order books
        '''
        orders_list = list(self.orders_dict.keys())
        for account, product, side in orders_list:
            self.process_cancel(account, product, side)