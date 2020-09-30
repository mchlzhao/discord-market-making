import sys

from controller_test import Controller
from util import Product

controller = Controller('Local Testing')

print('\nTYPE YOUR COMMANDS HERE:')
for line in sys.stdin:
    command = line.split()
    if command[0] == 'buy':
        account_id = command[1]
        product_order = int(command[2])
        price = int(command[3])

        result = controller.process_buy(account_id, product_order, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'sell':
        account_id = command[1]
        product_order = int(command[2])
        price = int(command[3])

        result = controller.process_sell(account_id, product_order, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'cancel':
        side = command[1][0]
        account_id = command[2]
        product_order = int(command[3])

        if side == 'b':
            result = controller.process_cancel_buy(account_id, product_order, True)
        else:
            result = controller.process_cancel_sell(account_id, product_order, True)
        print("return: %d" % result)
    elif command[0] == 'mark':
        product_order = int(command[1])
        did_occur = (command[2][0] == 'y')

        controller.mark_occurred(product_order, did_occur, True)
        print('marked', str(did_occur))
    else:
        print(command, 'not found')