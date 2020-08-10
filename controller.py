from engine import Engine
from sheet_interface import SheetInterface
from util import Account, Product, Side

import settings

products = settings.PRODUCTS

class Controller:
    def __init__(self):
        self.sheet_interface = SheetInterface()

        print('RAW ORDER BOOKS:')
        print(self.sheet_interface.order_books_raw)
        print('RAW ACCOUNTS:')
        print(self.sheet_interface.accounts_raw)
        print()

        self.accounts = []
        self.name_to_account = {}
        self.discord_id_to_account = {}

        self.engine = Engine(self.accounts, products, self.sheet_interface)
    
    def init_from_sheet(self):
        self.accounts = self.get_accounts_from_raw(self.sheet_interface.accounts_raw)
        for account in self.accounts:
            self.name_to_account[account.name] = account
            self.discord_id_to_account[account.discord_id] = account

        init_orders = self.get_orders_from_raw(self.sheet_interface.order_books_raw)
        for product, side, name, price in init_orders:
            self.engine.process_bid(self.name_to_account[name], product, side, price, False)
    
    def get_accounts_from_raw(self, accounts_raw):
        accounts_list = []
        for account_order, account_raw in enumerate(accounts_raw):
            cur_account = Account(int(account_raw[0]), account_raw[1], account_order, products)

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
    
    def add_account(self, discord_id, name):
        self.import_accounts([Account(discord_id, name, len(self.accounts), products)])
    
    def import_accounts(self, accounts):
        for account in accounts:
            self.name_to_account[account.name] = account
            self.discord_id_to_account[account.discord_id] = account
            self.accounts.append(account)
            self.sheet_interface.add_account(account)
        self.sheet_interface.batch_update()
    
    def process_bid(self, discord_id, product, side, price, do_write):
        return self.engine.process_bid(self.discord_id_to_account[discord_id], product, side, price, do_write)
    
    def process_cancel(self, discord_id, product, side, do_write):
        return self.engine.process_cancel(self.discord_id_to_account[discord_id], product, side, do_write)