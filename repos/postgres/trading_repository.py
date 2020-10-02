import psycopg2
from datetime import datetime
from typing import List, Tuple

from entities.instrument import Instrument
from entities.order import Order
from entities.side import Side
from entities.transaction import Transaction
from repos.trading_repository import TradingRepository

conn = psycopg2.connect(
    host = 'localhost',
    port = 5432,
    dbname = 'postgres',
    user = 'postgres',
    options='-c search_path="market_test"'
)

class PostgresTradingRepository(TradingRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_order(self, order: Order, status: str) -> None:
        query = '''INSERT INTO TradeOrder (account_id, instrument_id, side, price, order_time, status)
                VALUES (%s, %s, %s, %s, %s, %s)'''
        data = (order.account.account_id, order.instrument.id, order.side, order.price, datetime.now(), status)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def get_best_buy(self, instrument: Instrument, num_results: int = None) -> List[Tuple]:
        query = '''SELECT *
                FROM TradeOrder
                WHERE instrument_id = %s
                AND side = 'buy'
                AND status = 'unfilled'
                ORDER BY price DESC, order_time ASC
                LIMIT '''
        if num_results == None:
            query += 'ALL'
            data = (instrument.id, )
        else:
            query += '%s'
            data = (instrument.id, num_results)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchall()

    def get_best_sell(self, instrument: Instrument, num_results: int = None) -> List[Tuple]:
        query = '''SELECT *
                FROM TradeOrder
                WHERE instrument_id = %s
                AND side = 'sell'
                AND status = 'unfilled'
                ORDER BY price ASC, order_time ASC
                LIMIT '''
        if num_results == None:
            query += 'ALL'
            data = (instrument.id, )
        else:
            query += '%s'
            data = (instrument.id, num_results)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchall()

    def update_order_status(self, order: Order, status: str) -> None:
        query = '''UPDATE TradeOrder
                SET status = %s
                WHERE account_id = %s
                AND instrument_id = %s
                AND side = %s
                AND status = 'unfilled' '''
        data = (status, order.account.id, order.instrument.id, order.side)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def get_existing_order(self, account_id: str, display_order: int, side: Side) -> Tuple:
        query = '''SELECT *
                FROM TradeOrder
                JOIN Instrument ON TradeOrder.instrument_id = Instrument.id
                WHERE status = 'unfilled'
                AND account_id = %s
                AND display_order = %s
                AND is_active
                AND side = %s'''
        data = (account_id, display_order, side)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchone()

    def add_transaction(self, transaction: Transaction) -> None:
        query = '''INSERT INTO Transaction (transaction_time, buyer_id, seller_id, maker_side, instrument_id, price)
                VALUES (%s, %s, %s, %s, %s, %s)'''
        data = (datetime.now(), transaction.buyer_account.id, transaction.seller_account.id,
            'buy' if transaction.is_buyer_maker else 'sell', transaction.instrument.id, transaction.price)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
