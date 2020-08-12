import sys

from account import Account
from controller import Controller
from util import Side

import settings

accounts = [
    Account(0, 'alice', 0, settings.PRODUCTS),
    Account(1, 'bob', 1, settings.PRODUCTS),
    Account(2, 'charlie', 2, settings.PRODUCTS),
    Account(3, 'dave', 3, settings.PRODUCTS),
]

controller = Controller('Local Testing', 'local.log', settings.PRODUCTS)
controller.import_accounts(accounts, True)



controller.engine.print_order_books()
for account in controller.accounts:
    account.print_account()

print('\nTYPE YOUR COMMANDS HERE:')
for line in sys.stdin:
    command = line.split()
    if command[0] == 'buy':
        account_id = int(command[1])
        product_order = int(command[2])
        price = int(command[3])
        assert(product_order >= 1 and product_order <= len(settings.PRODUCTS))

        result = controller.process_bid(account_id, product_order, Side.BUY, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'sell':
        account_id = int(command[1])
        product_order = int(command[2])
        price = int(command[3])
        assert(product_order >= 1 and product_order <= len(settings.PRODUCTS))

        result = controller.process_bid(account_id, product_order, Side.SELL, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'cancel':
        side = command[1][0]
        account_id = int(command[2])
        product_order = int(command[3])
        assert(product_order >= 1 and product_order <= len(settings.PRODUCTS))

        result = controller.process_cancel(account_id, product_order, Side.BUY if side == 'b' else Side.SELL, True)
        print("return: %d" % result)
    elif command[0] == 'print':
        controller.engine.print_order_books()
    elif command[0] == 'mark':
        product_order = int(command[1])
        did_occur = (command[2][0] == 'y')
        assert(product_order >= 1 and product_order <= len(settings.PRODUCTS))

        controller.mark_occurred(product_order, did_occur, True)
        print('marked', str(did_occur))
    else:
        print(command, 'not found')