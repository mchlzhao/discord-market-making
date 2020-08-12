from account import Account
from engine import Engine
from sheet_interface import SheetInterface
from util import Side

import settings

class Controller:
    def __init__(self, sheet_name, products):
        self.sheet_interface = SheetInterface(sheet_name)

        self.accounts = []
        self.name_to_account = {}
        self.account_id_to_account = {}

        self.products = products
        self.product_order_to_product = {}
        for product in products:
            self.product_order_to_product[product.product_order] = product

        self.engine = Engine(self.accounts, self.products)
    
    def init_from_sheet(self):
        self.accounts = self.get_accounts_from_raw(self.sheet_interface.accounts_raw)
        for account in self.accounts:
            self.name_to_account[account.name] = account
            self.account_id_to_account[account.account_id] = account

        init_orders = self.get_orders_from_raw(self.sheet_interface.order_books_raw)
        for product, side, name, price in init_orders:
            self.process_bid(self.name_to_account[name].account_id, product.product_order+1, side, price, False)
    
    def get_accounts_from_raw(self, accounts_raw):
        accounts_list = []
        for account_order, account_raw in enumerate(accounts_raw):
            cur_account = Account(int(account_raw[0]), account_raw[1], account_order, self.products)
            cur_account.balance = int(account_raw[2])

            assert(len(account_raw) == 3+len(self.products))

            for product in self.products:
                cur_account.inventory[product] = int(account_raw[3 + product.product_order])
            
            accounts_list.append(cur_account)
        
        return accounts_list

    def get_orders_from_raw(self, order_books_raw):
        init_orders_list = []

        if len(order_books_raw) != len(self.products):
            print('NUMBER OF PRODUCTS DON\'T MATCH')
            print('expected %d    got %d' % (len(self.products), len(order_books_raw)))
            assert(False)

        for order, product_raw in enumerate(order_books_raw):
            for side, side_raw in enumerate(product_raw):
                for name, price in side_raw:
                    init_orders_list.append((self.product_order_to_product[order], Side(side), name, int(price)))

        return init_orders_list
    
    # error code: -1 = no more space
    def add_account(self, account_id, name):
        if len(self.accounts) >= settings.USER_LIMIT:
            return -1

        self.import_accounts([Account(account_id, name, len(self.accounts), self.products)])

        return 0
    
    def import_accounts(self, accounts):
        for account in accounts:
            self.name_to_account[account.name] = account
            self.account_id_to_account[account.account_id] = account
            self.accounts.append(account)
            self.sheet_interface.add_account(account)

        self.sheet_interface.batch_update()
    
    def has_user(self, account_id):
        return account_id in self.account_id_to_account
    
    # returns (error code, Transaction())
    # error codes: -1 = position limit breach    -2 = in cross with self   -3 = price not in bounds    -4 = product does not exist
    def process_bid(self, account_id, product_order, side, price, do_write):
        account = self.account_id_to_account[account_id]
        try:
            product = self.product_order_to_product[product_order-1]
        except KeyError:
            return (-4, 0)

        if price < 0 or price > 100:
            return (-3, None)

        if side == Side.BUY:
            if account.inventory[product] >= settings.POSITION_LIMIT:
                return (-1, None)

            existing = self.engine.account_has_existing_order(account, product, Side.SELL)
            if existing != -1 and existing <= price:
                return (-2, None)
        else:
            if account.inventory[product] <= -settings.POSITION_LIMIT:
                return (-1, None)

            existing = self.engine.account_has_existing_order(account, product, Side.BUY)
            if existing != -1 and existing >= price:
                return (-2, None)

        result = self.engine.process_bid(account, product, side, price)
        if result == None:
            # no transaction occurred
            if do_write:
                self.sheet_interface.update_order_book(product, side, self.engine.order_books[product].get_book_in_list(side))
        else:
            # transaction occurred
            result.buyer_account.process_transaction(product, Side.BUY, result.price)
            result.seller_account.process_transaction(product, Side.SELL, result.price)

            if do_write:
                self.sheet_interface.update_account(result.buyer_account)
                self.sheet_interface.update_account(result.seller_account)
                self.sheet_interface.update_order_book(product, Side.BUY, self.engine.order_books[product].get_book_in_list(Side.BUY))
                self.sheet_interface.update_order_book(product, Side.SELL, self.engine.order_books[product].get_book_in_list(Side.SELL))

        if do_write:
            self.sheet_interface.batch_update()

        return (0, result)
    
    # error codes: -1 = bid does not exist    -2 = product does not exist
    def process_cancel(self, account_id, product_order, side, do_write):
        account = self.account_id_to_account[account_id]
        try:
            product = self.product_order_to_product[product_order-1]
        except KeyError:
            return -2

        if self.engine.account_has_existing_order(account, product, side) == -1:
            return -1
        
        self.engine.process_cancel(account, product, side)

        if do_write:
            self.sheet_interface.update_order_book(product, side, self.engine.order_books[product].get_book_in_list(side))
            self.sheet_interface.batch_update()

        return 0
    
    # error codes: -1 = product does not exist
    def mark_occurred(self, product_order, did_occur, do_write):
        if did_occur == False:
            return 0
        
        try:
            product = self.product_order_to_product[product_order-1]
        except KeyError:
            return -1
        
        for account in self.accounts:
            account.balance += 100 * account.inventory[product]
            if do_write:
                self.sheet_interface.update_account(account)

        if do_write:
            self.sheet_interface.batch_update()
        
        return 0