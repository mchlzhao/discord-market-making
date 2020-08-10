import sys

from controller import Controller
from util import Account, Side

import settings

accounts = [
    Account(0, 'alice', 0, settings.PRODUCTS),
    Account(1, 'bob', 1, settings.PRODUCTS),
    Account(2, 'charlie', 2, settings.PRODUCTS),
    Account(3, 'dave', 3, settings.PRODUCTS),
]

controller = Controller('Local Testing')
controller.init_from_sheet()
# controller.import_accounts(accounts)



controller.engine.print_order_books()
for account in controller.accounts:
    account.print_account()

print('\nTYPE YOUR COMMANDS HERE:')
for line in sys.stdin:
    command = line.split()
    if command[0] == 'buy':
        discord_id = int(command[1])
        product_id = int(command[2])
        price = int(command[3])
        assert(product_id >= 1 and product_id <= len(settings.PRODUCTS))

        result = controller.process_bid(discord_id, settings.PRODUCTS[product_id-1], Side.BUY, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'sell':
        discord_id = int(command[1])
        product_id = int(command[2])
        price = int(command[3])
        assert(product_id >= 1 and product_id <= len(settings.PRODUCTS))

        result = controller.process_bid(discord_id, settings.PRODUCTS[product_id-1], Side.SELL, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'cancel':
        side = command[1][0]
        discord_id = int(command[2])
        product_id = int(command[3])
        assert(product_id >= 1 and product_id <= len(settings.PRODUCTS))

        result = controller.process_cancel(discord_id, settings.PRODUCTS[product_id-1], Side.BUY if side == 'b' else Side.SELL, True)
        print("return: %d" % result)
    elif command[0] == 'print':
        controller.engine.print_order_books()
    elif command[0] == 'mark':
        product_id = int(command[1])
        did_occur = (command[2][0] == 'y')
        assert(product_id >= 1 and product_id <= len(settings.PRODUCTS))

        controller.mark_occurred(product_id, did_occur)
        print('marked', str(did_occur))
    else:
        print(command, 'not found')