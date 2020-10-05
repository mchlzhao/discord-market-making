import sys

from controller_test import Controller

controller = Controller()

print('\nTYPE YOUR COMMANDS HERE:')
for line in sys.stdin:
    command = line.split()
    if command[0] == 'buy':
        account_id = command[1]
        product_order = int(command[2])
        price = int(command[3])

        result = controller.buy(account_id, product_order, price)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'sell':
        account_id = command[1]
        product_order = int(command[2])
        price = int(command[3])

        result = controller.sell(account_id, product_order, price)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'cancel':
        side = command[1][0]
        account_id = command[2]
        product_order = int(command[3])

        if side == 'b':
            result = controller.cancel_buy(account_id, product_order)
        else:
            result = controller.cancel_sell(account_id, product_order)
        print("return:", result)
    elif command[0] == 'mark':
        product_order = int(command[1])
        did_occur = (command[2][0] == 'y')

        result = controller.mark_occurred(product_order, did_occur)
        print("return:", result)
    elif command[0] == 'add':
        account_id = command[1]
        name = command[2]
        try:
            balance = command[3]
        except:
            balance = 0
        result = controller.add_account(account_id, name, balance)
        print("return:", result)
    elif command[0] == 'paybonus':
        controller.pay_bonus()
    elif command[0] == 'jsonaccount':
        print(controller.get_account_info())
    else:
        print(command, 'not found')
