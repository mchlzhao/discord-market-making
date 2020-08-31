import logging
import random

from account import Account
from engine import Engine
from sheet_interface import SheetInterface
from util import Product, Side

import input_parser
import settings

class Controller:
    def __init__(self, sheet_name, log_file_name, products = [], new_game = False):
        self.sheet_interface = SheetInterface(sheet_name)

        self.accounts = []
        self.name_to_account = {}
        self.id_to_account = {}

        self.products = products

        logging.basicConfig(
            filename = log_file_name, 
            level = logging.INFO,
            format = '%(asctime)s:%(levelname)s:%(message)s'
        )

        if new_game:
            pass
        else:
            '''
            if loading existing game, the accounts and the products are both taken from the sheet
            '''
            for i in range(len(self.sheet_interface.order_books_raw)):
                self.products.append(Product(i+1, i, 'E'+str(i)))

            self.import_accounts(input_parser.get_accounts_from_raw(self.sheet_interface.accounts_raw, self.products), False)

            logging.info('Initialised from sheet:')
            for account in self.accounts:
                logging.info('%d %s %d: %d' % (account.id, account.name, account.account_order, account.balance))
                logging.info(' '.join(map(lambda x: str(x[1]), account.inventory.items())))

        self.engine = Engine(self.products)

        if not new_game:
            init_orders = input_parser.get_orders_from_raw(self.sheet_interface.order_books_raw, self.products)
            for product, side, name, price in init_orders:
                self.process_bid(self.name_to_account[name].id, product.product_order+1, side, price, False)

        logging.info('Controller initialised\n')
    
    def __del__(self):
        logging.info('Controller stopping:')
        for account in self.accounts:
            logging.info('%d %s %d: %d' % (account.id, account.name, account.account_order, account.balance))
            logging.info(' '.join(map(lambda x: str(x[1]), account.inventory.items())))
        logging.info('Controller stopped\n')
    
    def init_from_sheet(self):
        '''
        loads parsed accounts and orders into the controller, restoring the state
        '''
        pass
    
    def add_account(self, account_id, name, do_write):
        '''
        wrapper for self.import_accounts()
        creates new account with account_id and name
        '''
        return self.import_accounts([Account(account_id, name, len(self.accounts), self.products)], do_write)
    
    def import_accounts(self, accounts, do_write):
        '''
        imports existing Account objects into the controller
        pushes new Account to the spreadsheet
        return:
            -1 if USER_LIMIT is breached
            0 otherwise
        '''
        if len(self.accounts) + len(accounts) > settings.USER_LIMIT:
            return -1

        for account in accounts:
            self.name_to_account[account.name] = account
            self.id_to_account[account.id] = account
            self.accounts.append(account)

            if do_write:
                self.sheet_interface.update_account(account)

        if do_write:
            self.sheet_interface.batch_update()
        
        return 0
    
    def has_user(self, account_id):
        return account_id in self.id_to_account
    
    def process_bid(self, account_id, product_order, side, price, do_write):
        '''
        inserts a bid
        if price is in cross with any existing order, price is automatically clamped at the existing price by the engine
        return: (error code, Transaction)
            -1 if position limit of Account breached
            -2 if order is in cross with another order by the same account
            -3 if price is not within bounds
            -4 if product_order does not exist
            -5 if account_id does not exist
            0 otherwise

            returns Transaction if a trade occurs, None otherwise
        '''
        try:
            account = self.id_to_account[account_id]
        except KeyError:
            return (-5, 0)
        try:
            if product_order < 1:
                raise IndexError
            product = self.products[product_order-1]
        except (IndexError, TypeError):
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

        logging.info('%s %s %s %d', side.name, account.name, product.description, price)

        if do_write:
            self.sheet_interface.update_order_book(self.engine.order_books[product])

        if result != None:
            result.buyer_account.process_transaction(product, Side.BUY, result.price)
            result.seller_account.process_transaction(product, Side.SELL, result.price)

            logging.info('TRADE %s->%s %s %d', result.seller_account.name, result.buyer_account.name, product.description, result.price)

            if do_write:
                self.sheet_interface.update_account(result.buyer_account)
                self.sheet_interface.update_account(result.seller_account)

        if do_write:
            self.sheet_interface.batch_update()

        return (0, result)
    
    def process_buy(self, account_id, product_order, price, do_write):
        '''
        wrapper for process_bid buy
        '''
        return self.process_bid(account_id, product_order, Side.BUY, price, do_write)
    
    def process_sell(self, account_id, product_order, price, do_write):
        '''
        wrapper for process_bid sell
        '''
        return self.process_bid(account_id, product_order, Side.SELL, price, do_write)
    
    def process_cancel(self, account_id, product_order, side, do_write):
        '''
        cancels a bid
        return:
            -1 if there does not exist an existing bid by this account for this product on this side
            -2 if product_order does not exist
            -3 if account_id does not exist
            0 otherwise
        '''
        try:
            account = self.id_to_account[account_id]
        except KeyError:
            return -3
        try:
            if product_order < 1:
                raise IndexError
            product = self.products[product_order-1]
        except (IndexError, TypeError):
            return -2

        if self.engine.account_has_existing_order(account, product, side) == -1:
            return -1
        
        self.engine.process_cancel(account, product, side)

        logging.info('CANCEL %s %s %s', side.name, account.name, product.description)

        if do_write:
            self.sheet_interface.update_order_book(self.engine.order_books[product])
            self.sheet_interface.batch_update()

        return 0
    
    def process_cancel_buy(self, account_id, product_order, do_write):
        '''
        wrapper for process_cancel buy
        '''
        return self.process_cancel(account_id, product_order, Side.BUY, do_write)

    def process_cancel_sell(self, account_id, product_order, do_write):
        '''
        wrapper for process_cancel sell
        '''
        return self.process_cancel(account_id, product_order, Side.SELL, do_write)
    
    def mark_occurred(self, product_order, did_occur, do_write):
        '''
        called when the result of a product has been settled
        for binary options, sellers pay buyers $100 if event did occur, nothing otherwise
        return:
            -1 if product_order does not exist
            0 otherwise
        '''
        try:
            if product_order < 1:
                raise IndexError
            product = self.products[product_order-1]
        except (IndexError, TypeError):
            return -1

        logging.info('MARK %s %s', product.description, did_occur)

        if did_occur == False:
            return 0
        
        for account in self.accounts:
            account.balance += 100 * account.inventory[product]
            if do_write:
                self.sheet_interface.update_account(account)

        if do_write:
            self.sheet_interface.batch_update()
        
        return 0
    
    def get_accounts_most_pos(self):
        '''
        returns the list of accounts, sorted in descending order of total positions
        used for paying out bonuses for taking risk
        ties are broken by random
        '''
        num_positions = {}
        for account in self.accounts:
            num_positions.setdefault(account.total_positions, []).append(account)
        
        ordered_accounts = []
        for _, accounts_list in sorted(num_positions.items()):
            temp = list(accounts_list)
            random.shuffle(temp)
            ordered_accounts.extend(temp)
        
        return list(reversed(ordered_accounts))
    
    def pay_bonus(self):
        '''
        pays bonuses to players based on order from self.get_accounts_most_pos()
        returns list of pairs of accounts and their received payouts
        '''
        ordered_accounts = self.get_accounts_most_pos()
        bonuses = [75, 60, 45, 30, 15, 0]

        payouts = []
        for account, bonus in zip(ordered_accounts, bonuses):
            payouts.append([account, bonus])
            account.balance += bonus

            self.sheet_interface.update_account(account)
            logging.info('%s has %d positions, will be paid %d', account.name, account.total_positions, bonus)
        
        self.sheet_interface.batch_update()

        return payouts
    
    def clear_orders(self):
        '''
        clears all orders from all order books
        '''
        logging.info('clearing all orders')

        self.engine.clear_orders()

        for product in self.products:
            self.sheet_interface.update_order_book(self.engine.order_books[product])
        
        self.sheet_interface.batch_update()
    
    def clear_positions(self):
        '''
        clears all positions held by accounts
        '''
        logging.info('clearing all positions')

        for account in self.accounts:
            for product in account.products:
                account.add_inventory(product, -account.inventory[product])
            
            self.sheet_interface.update_account(account)
        
        self.sheet_interface.batch_update()