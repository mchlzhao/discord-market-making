from test import *

def is_buy_in_cross(account_id, display_order, price):
    existing_sell = get_existing_order(account_id, display_order, 'sell')
    return existing_sell is not None and existing_sell[4] <= price

def is_sell_in_cross(account_id, display_order, price):
    existing_buy = get_existing_order(account_id, display_order, 'buy')
    return existing_buy is not None and price <= existing_buy[4]

# assumes buys do not cross with existing sells
def process_buy(account_id, display_order, price):
    existing = get_existing_order(account_id, display_order, 'buy')
    if existing is not None:
        update_order_status_using_display_order(account_id, display_order, 'buy', 'cancelled')

    try:
        best_sell = get_best_sell_using_display_order(display_order, num_results = 1)[0]
    except IndexError:
        best_sell = None
    print(best_sell)

    if best_sell is None or price < best_sell[4]:
        add_order_using_display_order(account_id, display_order, 'buy', price, 'unfilled')
        return None
    
    add_order_using_display_order(account_id, display_order, 'buy', best_sell[4], 'filled')
    update_order_status_using_display_order(best_sell[2], display_order, 'sell', 'filled')

    print('%s bought from %s instrument display order = %d price = %d' % (account_id, best_sell[2], best_sell[5], best_sell[4]))
    return None

process_buy('a', 1, 80)