from util import Side
from order_book import OrderBook

import settings

class Engine:
    def __init__(self, accounts, products, sheet_writer):
        self.accounts = accounts
        self.products = products

        self.order_books = {product: OrderBook(product) for product in products}
        self.orders_by_account = {}

        self.transaction_history = []

        self.sheet_writer = sheet_writer
    
    def account_has_existing_order(self, account, product, side):
        if (account, product, side) not in self.orders_by_account:
            return -1
        return self.orders_by_account[(account, product, side)]
    
    # return -1: in cross with existing trade from same account
    # return -2: account is at position limit
    # must ensure price is integer and between [0, 100]
    def process_bid(self, account, product, side, price, do_write):
        order_book = self.order_books[product]

        if account.inventory[product] >= settings.POSITION_LIMIT and side == Side.BUY or \
                account.inventory[product] <= -settings.POSITION_LIMIT and side == Side.SELL:
            return (-2, None)

        if side == Side.BUY:
            lowest_sell = order_book.get_best_sell_price()
            price = min(price, lowest_sell)
            if self.account_has_existing_order(account, product, Side.SELL) == price:
                return (-1, None)
        else:
            highest_buy = order_book.get_best_buy_price()
            price = max(price, highest_buy)
            if self.account_has_existing_order(account, product, Side.BUY) == price:
                return (-1, None)

        if self.account_has_existing_order(account, product, side) > -1:
            self.process_cancel(account, product, side, False)
        
        self.orders_by_account[(account, product, side)] = price
        order_book.add_order(account, side, price)

        match = order_book.test_if_match(price)

        if match != None:
            self.transaction_history.append(match)
            match.buyer_account.balance -= match.price
            match.buyer_account.inventory[match.product] += 1
            self.orders_by_account.pop((match.buyer_account, match.product, Side.BUY))
            match.seller_account.balance += match.price
            match.seller_account.inventory[match.product] -= 1
            self.orders_by_account.pop((match.seller_account, match.product, Side.SELL))

            if do_write:
                self.sheet_writer.update_account(match.buyer_account)
                self.sheet_writer.update_account(match.seller_account)

        if do_write:
            self.sheet_writer.update_order_book(product, Side.BUY, order_book.get_book_in_list(Side.BUY))
            self.sheet_writer.update_order_book(product, Side.SELL, order_book.get_book_in_list(Side.SELL))
            self.sheet_writer.batch_update()

        return (0, match)
    
    # return -1: no existing order to cancel
    def process_cancel(self, account, product, side, do_write):
        order_book = self.order_books[product]
        if order_book.remove_account(account, side) == -1:
            return -1

        if do_write:
            self.sheet_writer.update_order_book(product, side, order_book.get_book_in_list(side))
            self.sheet_writer.batch_update()

        self.orders_by_account.pop((account, product, side))
        return 0
    
    def mark_occurred(self, product, did_occur):
        if did_occur == False:
            return
        for account in self.accounts:
            account.balance += 100*account.inventory[product]
            if account.inventory[product] != 0:
                self.sheet_writer.update_account(account)
        self.sheet_writer.batch_update()
    
    def print_order_books(self):
        for product, book in self.order_books.items():
            print(product.description)
            print(list(map(lambda x: (x[0].name, x[1]), book.get_book_in_list(Side.BUY))))
            print(list(map(lambda x: (x[0].name, x[1]), book.get_book_in_list(Side.SELL))))
            print()
        
        for key, value in self.orders_by_account.items():
            print(key[0].name, key[1].product_id, int(key[2]), value)