import sys
import psycopg2

from controller_test import Controller
from util import Product
from entities.side import Side

from engine_test import Engine

from repos.postgres.account_repository import PostgresAccountRepository
from repos.postgres.instrument_repository import PostgresInstrumentRepository
from repos.postgres.position_repository import PostgresPositionRepository
from repos.postgres.trading_repository import PostgresTradingRepository

conn = psycopg2.connect(
    host = 'localhost',
    port = 5432,
    dbname = 'postgres',
    user = 'postgres',
    options='-c search_path="market_test"'
)
account_repository = PostgresAccountRepository(conn)
instrument_repository = PostgresInstrumentRepository(conn)
position_repository = PostgresPositionRepository(conn)
trading_repository = PostgresTradingRepository(conn)

controller = Engine(account_repository, instrument_repository,
    position_repository, trading_repository)

print('\nTYPE YOUR COMMANDS HERE:')
for line in sys.stdin:
    command = line.split()
    if command[0] == 'buy':
        account_id = command[1]
        product_order = int(command[2])
        price = int(command[3])

        result = controller.process_buy(account_id, product_order, price)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'sell':
        account_id = command[1]
        product_order = int(command[2])
        price = int(command[3])

        result = controller.process_sell(account_id, product_order, price)
        print('return: %d %s' % (result[0], str(result[1]) if result[1] is not None else '-'))
    elif command[0] == 'cancel':
        side = command[1][0]
        account_id = command[2]
        product_order = int(command[3])

        if side == 'b':
            result = controller.process_cancel(account_id, product_order, Side.BUY)
        else:
            result = controller.process_cancel(account_id, product_order, Side.SELL)
        print("return:", result)
    elif command[0] == 'mark':
        product_order = int(command[1])
        did_occur = (command[2][0] == 'y')

        # controller.mark_occurred(product_order, did_occur, True)
        print('marked', str(did_occur))
    else:
        print(command, 'not found')