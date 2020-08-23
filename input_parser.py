from account import Account
from util import Side

def get_accounts_from_raw(accounts_raw, products):
    '''
    parses raw account data
    return: list of Account
    '''
    accounts_list = []
    for account_order, account_raw in enumerate(accounts_raw):
        cur_account = Account(int(account_raw[0]), account_raw[1], account_order, products)
        cur_account.balance = int(account_raw[2])

        assert(len(account_raw) == 3+len(products))

        for product in products:
            cur_account.add_inventory(product, int(account_raw[3 + product.product_order]))
        
        accounts_list.append(cur_account)
    
    return accounts_list

def get_orders_from_raw(order_books_raw, products):
    '''
    parses raw order book data
    return: list of (Product, Side, name, price)
    '''
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