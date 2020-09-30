from util import Side
from test import *

class Engine:
    def is_buy_in_cross(self, account_id, display_order, price):
        existing_sell = get_existing_order(account_id, display_order, 'sell')
        return existing_sell is not None and existing_sell[4] <= price

    def is_sell_in_cross(self, account_id, display_order, price):
        existing_buy = get_existing_order(account_id, display_order, 'buy')
        return existing_buy is not None and price <= existing_buy[4]
    
    def process_bid(self, account_id, display_order, side, price):
        if side == Side.BUY:
            return self.process_buy(account_id, display_order, price)
        
        return self.process_sell(account_id, display_order, price)

    # assumes buys do not cross with existing sells
    def process_buy(self, account_id, display_order, price):
        existing = get_existing_order(account_id, display_order, 'buy')
        if existing is not None:
            self.process_cancel(account_id, display_order, 'buy')

        try:
            best_sell = get_best_sell_using_display_order(display_order, num_results = 1)[0]
        except IndexError:
            best_sell = None
        print('best sell =', best_sell)

        if best_sell is None or price < best_sell[4]:
            add_order_using_display_order(account_id, display_order, 'buy', price, 'unfilled')
            return None
        
        add_order_using_display_order(account_id, display_order, 'buy', best_sell[4], 'filled')
        update_order_status_using_display_order(best_sell[2], display_order, 'sell', 'filled')

        print('%s bought from %s instrument display order = %d price = %d' %
            (account_id, best_sell[2], best_sell[5], best_sell[4]))
        
        return {
            'buyer_id': account_id,
            'seller_id': best_sell[2],
            'is_buyer_maker': False,
            'instrument_id': best_sell[5],
            'display_order': display_order,
            'price': best_sell[4]
        }

    def process_sell(self, account_id, display_order, price):
        existing = get_existing_order(account_id, display_order, 'sell')
        if existing is not None:
            self.process_cancel(account_id, display_order, 'sell')
        
        try:
            best_buy = get_best_buy_using_display_order(display_order, num_results = 1)[0]
        except IndexError:
            best_buy = None
        print('best buy =', best_buy)

        if best_buy is None or best_buy[4] < price:
            add_order_using_display_order(account_id, display_order, 'sell', price, 'unfilled')
            return None
        
        add_order_using_display_order(account_id, display_order, 'sell', best_buy[4], 'filled')
        update_order_status_using_display_order(best_buy[2], display_order, 'buy', 'filled')

        print('%s sold to %s instrument display order = %d price = %d' % 
            (account_id, best_buy[2], best_buy[5], best_buy[4]))

        return {
            'buyer_id': best_buy[2],
            'seller_id': account_id,
            'is_buyer_maker': True,
            'instrument_id': best_buy[5],
            'display_order': display_order,
            'price': best_buy[4]
        }

    def process_cancel(self, account_id, display_order, side):
        update_order_status_using_display_order(account_id, display_order, side, 'cancelled')
