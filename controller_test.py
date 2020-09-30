import random

from engine_test import Engine
from sheet_interface import SheetInterface
from util import Side
from test import *

import settings

class Controller:
    def __init__(self, sheet_name, new_game = False):
        self.sheet_interface = SheetInterface(sheet_name)

        self.engine = Engine()
    
    def add_account(self, account_id, name, do_write):
        '''
        wrapper for self.import_accounts()
        creates new account with account_id and name
        '''
        add_account(account_id, name)
    
    def process_bid(self, account_id, display_order, side, price, do_write):
        '''
        inserts a bid
        if price is in cross with any existing order, price is automatically clamped at the existing price by the engine
        return: (error code, Transaction)
            -1 if position limit of Account breached
            -2 if order is in cross with another order by the same account
            -3 if price is not within bounds
            -4 if display_order does not exist
            -5 if account_id does not exist
            0 otherwise

            returns Transaction if a trade occurs, None otherwise
        '''
        if price < 0 or price > 100:
            return (-3, None)

        if side == Side.BUY:
            if get_position(account_id, display_order) >= settings.POSITION_LIMIT:
                return (-1, None)
            
            if self.engine.is_buy_in_cross(account_id, display_order, price):
                return (-2, None)
        else:
            if get_position(account_id, display_order) <= -settings.POSITION_LIMIT:
                return (-1, None)
            
            if self.engine.is_sell_in_cross(account_id, display_order, price):
                return (-2, None)

        result = self.engine.process_bid(account_id, display_order, side, price)

        if result != None:
            update_position_using_display_order(result['buyer_id'], display_order, 1)
            update_position_using_display_order(result['seller_id'], display_order, -1)
            increment_account_balance(result['buyer_id'], -result['price'])
            increment_account_balance(result['seller_id'], result['price'])
            add_transaction(result['buyer_id'], result['seller_id'], result['is_buyer_maker'], result['instrument_id'], result['price'])

        return (0, result)
    
    def process_buy(self, account_id, display_order, price, do_write):
        '''
        wrapper for process_bid buy
        '''
        return self.process_bid(account_id, display_order, Side.BUY, price, do_write)
    
    def process_sell(self, account_id, display_order, price, do_write):
        '''
        wrapper for process_bid sell
        '''
        return self.process_bid(account_id, display_order, Side.SELL, price, do_write)
    
    def process_cancel(self, account_id, display_order, side, do_write):
        '''
        cancels a bid
        return:
            -1 if there does not exist an existing bid by this account for this product on this side
            -2 if display_order does not exist
            -3 if account_id does not exist
            0 otherwise
        '''
        if get_existing_order(account_id, display_order, 'buy' if side == Side.BUY else 'sell') is None:
            return -1
        
        self.engine.process_cancel(account_id, display_order, 'buy' if side == Side.BUY else 'sell')

        return 0
    
    def process_cancel_buy(self, account_id, display_order, do_write):
        '''
        wrapper for process_cancel buy
        '''
        return self.process_cancel(account_id, display_order, Side.BUY, do_write)

    def process_cancel_sell(self, account_id, display_order, do_write):
        '''
        wrapper for process_cancel sell
        '''
        return self.process_cancel(account_id, display_order, Side.SELL, do_write)
    
    def mark_occurred(self, display_order, did_occur, do_write):
        '''
        called when the result of a product has been settled
        for binary options, sellers pay buyers $100 if event did occur, nothing otherwise
        return:
            -1 if display_order does not exist
            0 otherwise
        '''
        if not did_occur:
            return

        all_positions = get_all_positions_using_display_order(display_order)
        print(all_positions)

        for account_id, num_positions in all_positions:
            increment_account_balance(account_id, 100 * num_positions)
    
    def get_accounts_most_pos(self):
        '''
        returns the list of accounts, sorted in descending order of total positions
        used for paying out bonuses for taking risk
        ties are broken by random
        '''
        pass
    
    def pay_bonus(self):
        '''
        pays bonuses to players based on order from self.get_accounts_most_pos()
        returns list of pairs of accounts and their received payouts
        '''
        pass
    
    def clear_orders(self):
        '''
        clears all orders from all order books
        '''
        pass

    def clear_positions(self):
        '''
        clears all positions held by accounts
        '''
        pass

