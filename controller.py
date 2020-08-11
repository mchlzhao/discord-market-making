from account import Account
from engine import Engine
from sheet_interface import SheetInterface
from util import Product, Side

import settings

products = settings.PRODUCTS

class Controller:
    def __init__(self, sheet_name):
        self.sheet_interface = SheetInterface(sheet_name)

        print('RAW ORDER BOOKS:')
        print(self.sheet_interface.order_books_raw)
        print('RAW ACCOUNTS:')
        print(self.sheet_interface.accounts_raw)
        print()

        self.accounts = []
        self.name_to_account = {}
        self.discord_id_to_account = {}

        self.engine = Engine(self.accounts, products)
    
    def init_from_sheet(self):
        self.accounts = self.get_accounts_from_raw(self.sheet_interface.accounts_raw)
        for account in self.accounts:
            self.name_to_account[account.name] = account
            self.discord_id_to_account[account.discord_id] = account

        init_orders = self.get_orders_from_raw(self.sheet_interface.order_books_raw)
        for product, side, name, price in init_orders:
            self.process_bid(self.name_to_account[name].discord_id, product.product_id, side, price, False)
    
    def get_accounts_from_raw(self, accounts_raw):
        accounts_list = []
        for account_order, account_raw in enumerate(accounts_raw):
            cur_account = Account(int(account_raw[0]), account_raw[1], account_order)

            cur_account.balance = int(account_raw[2])
            assert(len(account_raw) == 3+len(products))
            for product_order in range(len(products)):
                cur_account.inventory[products[product_order]] = int(account_raw[3+product_order])
            
            accounts_list.append(cur_account)
        
        return accounts_list

    def get_orders_from_raw(self, order_books_raw):
        init_orders_list = []
        if len(order_books_raw) != len(products):
            print('NUMBER OF PRODUCTS DON\'T MATCH')
            print('expected %d    got %d' % (len(products), len(order_books_raw)))
            assert(False)

        for order, product_raw in enumerate(order_books_raw):
            for side, side_raw in enumerate(product_raw):
                for name, price in side_raw:
                    init_orders_list.append((products[order], Side(side), name, int(price)))

        return init_orders_list
    
    # error code: -1 = no more space
    def add_account(self, discord_id, name):
        if len(self.accounts) >= settings.USER_LIMIT:
            return -1

        self.import_accounts([Account(discord_id, name, len(self.accounts))])
        return 0
    
    def import_accounts(self, accounts):
        for account in accounts:
            self.name_to_account[account.name] = account
            self.discord_id_to_account[account.discord_id] = account
            self.accounts.append(account)
            self.sheet_interface.add_account(account)

        self.sheet_interface.batch_update()
    
    def has_user(self, discord_id):
        return discord_id in self.discord_id_to_account
    
    # returns (error code, Transaction())
    # error codes: -1 = position limit breach    -2 = in cross with self   -3 = price not in bounds
    def process_bid(self, discord_id, product_id, side, price, do_write):
        account = self.discord_id_to_account[discord_id]
        product = products[product_id-1]

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

            result.buyer_account.balance -= result.price
            result.buyer_account.inventory[product] += 1
            result.seller_account.balance += result.price
            result.seller_account.inventory[product] -= 1

            if do_write:
                self.sheet_interface.update_account(result.buyer_account)
                self.sheet_interface.update_account(result.seller_account)
                self.sheet_interface.update_order_book(product, Side.BUY, self.engine.order_books[product].get_book_in_list(Side.BUY))
                self.sheet_interface.update_order_book(product, Side.SELL, self.engine.order_books[product].get_book_in_list(Side.SELL))

        if do_write:
            self.sheet_interface.batch_update()

        return (0, result)
    
    # error codes: -1 = bid does not exist
    def process_cancel(self, discord_id, product_id, side, do_write):
        account = self.discord_id_to_account[discord_id]
        product = products[product_id-1]

        if self.engine.account_has_existing_order(account, product, side) == -1:
            return -1
        
        self.engine.process_cancel(account, product, side)

        if do_write:
            self.sheet_interface.update_order_book(product, side, self.engine.order_books[product].get_book_in_list(side))
            self.sheet_interface.batch_update()

        return 0
    
    def mark_occurred(self, product_id, did_occur, do_write):
        if did_occur == False:
            return
        
        for account in self.accounts:
            account.balance += 100 * account.inventory[products[product_id-1]]
            if do_write:
                self.sheet_interface.update_account(account)

        if do_write:
            self.sheet_interface.batch_update()