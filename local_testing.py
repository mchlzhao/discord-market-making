import sys

from controller import Controller
from util import Account, Side

import settings

accounts = [
    Account('a', 'alice', 0, settings.PRODUCTS),
    Account('b', 'bob', 1, settings.PRODUCTS),
    Account('c', 'charlie', 2, settings.PRODUCTS),
    Account('d', 'dave', 3, settings.PRODUCTS),
]

controller = Controller()
controller.import_accounts(accounts)



controller.engine.print_order_books()
for account in controller.accounts:
    account.print_account()

print('\nTYPE YOUR COMMANDS HERE:')
for line in sys.stdin:
    command = line.split()
    if command[0] == 'buy':
        discord_id = command[1]
        product_id = int(command[2])
        price = int(command[3])
        assert(price >= 0 and price <= 100)
        assert(product_id >= 1 and product_id <= len(settings.PRODUCTS))

        result = controller.process_bid(discord_id, settings.PRODUCTS[product_id-1], Side.BUY, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'sell':
        discord_id = command[1]
        product_id = int(command[2])
        price = int(command[3])
        assert(price >= 0 and price <= 100)
        assert(product_id >= 1 and product_id <= len(settings.PRODUCTS))

        result = controller.process_bid(discord_id, settings.PRODUCTS[product_id-1], Side.SELL, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'cancel':
        print('cancel')
        pass
    elif command[0] == 'print':
        controller.engine.print_order_books()
    else:
        print(command, 'not found')