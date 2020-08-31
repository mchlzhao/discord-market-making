import sys

from account import Account
from controller import Controller
from util import Product

products = [
    Product(1, 0, 'E1'),
    Product(2, 1, 'E2'),
    Product(3, 2, 'E3'),
    Product(4, 3, 'E4'),
    Product(5, 4, 'E5'),
    Product(6, 5, 'E6'),
    Product(7, 6, 'E7'),
    Product(8, 7, 'E8'),
]

accounts = [
    Account(0, 'alice', 0, products),
    Account(1, 'bob', 1, products),
    Account(2, 'charlie', 2, products),
    Account(3, 'dave', 3, products),
]

controller = Controller('Local Testing', 'app_local.log', products, True)
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
        assert(product_order >= 1 and product_order <= len(products))

        result = controller.process_buy(account_id, product_order, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'sell':
        account_id = int(command[1])
        product_order = int(command[2])
        price = int(command[3])
        assert(product_order >= 1 and product_order <= len(products))

        result = controller.process_sell(account_id, product_order, price, True)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'cancel':
        side = command[1][0]
        account_id = int(command[2])
        product_order = int(command[3])
        assert(product_order >= 1 and product_order <= len(products))

        if side == 'b':
            result = controller.process_cancel_buy(account_id, product_order, True)
        else:
            result = controller.process_cancel_sell(account_id, product_order, True)
        print("return: %d" % result)
    elif command[0] == 'print':
        controller.engine.print_order_books()
    elif command[0] == 'mark':
        product_order = int(command[1])
        did_occur = (command[2][0] == 'y')
        assert(product_order >= 1 and product_order <= len(products))

        controller.mark_occurred(product_order, did_occur, True)
        print('marked', str(did_occur))
    else:
        print(command, 'not found')