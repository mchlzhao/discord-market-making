import time

from engine import Engine
from util import Product, Account, Side
from sheet_interface import SheetInterface

from settings import PRODUCTS as products

ORDER_BOOK_ROW = 2
ORDER_BOOK_COL = 2

ACCOUNT_ROW = 2
ACCOUNT_COL = 15

USER_LIMIT = 10

order_book_c1 = chr(ord('A') + ORDER_BOOK_COL + 1)
order_book_c2 = chr(ord(order_book_c1) + USER_LIMIT - 1)

accounts = []
account_from_name = dict()

def init_accounts_from_sheet(sheet_data):
    cur_row = ACCOUNT_ROW-1
    cur_col = ACCOUNT_COL
    assert(sheet_data[cur_row][cur_col-1] == 'Accounts')
    while cur_col < len(sheet_data[cur_row]) and sheet_data[cur_row][cur_col] != '':
        discord_id = int(sheet_data[cur_row][cur_col])
        name = sheet_data[cur_row+1][cur_col]
        balance = int(sheet_data[cur_row+2][cur_col])

        accounts.append(Account(discord_id, name, cur_col-ACCOUNT_COL, products))
        accounts[-1].balance = balance
        account_from_name[name] = accounts[-1]

        cur_row += 3
        for product in products:
            accounts[-1].inventory[product] = int(sheet_data[cur_row][cur_col])
            cur_row += 1

        cur_row = ACCOUNT_ROW-1
        cur_col += 1

def init_books_from_sheet(sheet_data, engine):
    num_products = 0
    cur_row = ORDER_BOOK_ROW
    while cur_row < len(sheet_data) and sheet_data[cur_row][1].split()[0] == 'Event':
        num_products += 1
        cur_row += 5
    if num_products != len(products):
        print('Number of products don\'t match')
        assert(False)
    
    cur_row = ORDER_BOOK_ROW-1
    cur_col = ORDER_BOOK_COL+1

    for product in products:
        for side in [Side.BUY, Side.SELL]:
            while cur_col < len(sheet_data[cur_row]) and sheet_data[cur_row][cur_col] != '':
                name = sheet_data[cur_row][cur_col]
                price = int(sheet_data[cur_row+1][cur_col])
                account = account_from_name[name]

                engine.process_bid(account, product, side, price, False)

                cur_col += 1

            cur_row += 2
            cur_col = ORDER_BOOK_COL+1

        cur_row += 1
        cur_col = ORDER_BOOK_COL+1

def add_account(sheet_writer, discord_id, name):
    accounts.append(Account(discord_id, name, len(accounts), products))
    sheet_writer.add_account(accounts[-1])
    sheet_writer.batch_update()

def test(engine):
    print(engine.process_bid(accounts[0], products[0], Side.BUY, 50, True))
    time.sleep(10)
    print(engine.process_bid(accounts[0], products[0], Side.SELL, 51, True))
    time.sleep(10)
    print(engine.process_bid(accounts[1], products[0], Side.BUY, 40, True))
    time.sleep(10)
    print(engine.process_bid(accounts[0], products[0], Side.BUY, 39, True))
    time.sleep(10)
    print(engine.process_bid(accounts[1], products[0], Side.BUY, 51, True))
    time.sleep(10)
    add_account(engine.sheet_writer, 'd', 'Daniel')

    for account in accounts:
        account.print_account()
    
    for product in products:
        engine.mark_occurred(product, False)

    time.sleep(10)
    
    for account in accounts:
        account.print_account()

def main(position_limit):
    sheet_writer = SheetInterface()
    sheet_data = sheet_writer.main_sheet.get_all_values()
    init_accounts_from_sheet(sheet_data)
    engine = Engine(accounts, products, sheet_writer, position_limit)
    init_books_from_sheet(sheet_data, engine)
    return engine

def test_reader():
    sheet_interface = SheetInterface()
    for product in sheet_interface.order_books_raw:
        for side in product:
            print(side)
        print()
    
    for account in sheet_interface.accounts_raw:
        print(account)
        print()

if __name__ == '__main__':
    test_reader()