import psycopg2

from repos.postgres.trading_repository import PostgresTradingRepository

from entities.order import Order
from entities.order_status import OrderStatus
from entities.side import Side

conn = psycopg2.connect(
    host = 'localhost',
    port = 5432,
    dbname = 'postgres',
    user = 'postgres',
    options='-c search_path="market_test"'
)

repo = PostgresTradingRepository(conn)

res = repo.get_best_sell_using_instrument_id(1)
for i in res:
    print(i)
print()

repo.update_order_status_using_instrument_id('a', 1, Side.SELL, OrderStatus.CANCELLED)

res = repo.get_best_sell_using_instrument_id(1)
for i in res:
    print(i)
print()
