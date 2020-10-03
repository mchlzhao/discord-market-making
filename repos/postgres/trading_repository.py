import psycopg2
from datetime import datetime
from typing import List, Tuple

from entities.account import Account
from entities.instrument import Instrument
from entities.order import Order
from entities.side import Side
from entities.transaction import Transaction

from repos.trading_repository import ITradingRepository

class PostgresTradingRepository(ITradingRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_order(self, order: Order, status: str) -> None:
        query = '''INSERT INTO TradeOrder (account_id, instrument_id, side, price, order_time, status)
                VALUES (%s, %s, %s, %s, %s, %s)'''
        data = (order.account_id, order.instrument_id, str(order.side), order.price, datetime.now(), status)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
    
    def get_best_buy_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price
                FROM TradeOrder
                JOIN Instrument ON TradeOrder.instrument_id = Instrument.id
                JOIN Account ON TradeOrder.account_id = Account.id
                WHERE display_order = %s
                AND is_active
                AND side = 'buy'
                AND status = 'unfilled'
                ORDER BY price DESC, order_time ASC
                LIMIT '''
        if num_results == None:
            query += 'ALL'
            data = (display_order, )
        else:
            query += '%s'
            data = (display_order, num_results)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return list(map(Order.from_tuple, cur.fetchall()))

    def get_best_buy_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price
                FROM TradeOrder
                WHERE instrument_id = %s
                AND side = 'buy'
                AND status = 'unfilled'
                ORDER BY price DESC, order_time ASC
                LIMIT '''
        if num_results == None:
            query += 'ALL'
            data = (instrument_id, )
        else:
            query += '%s'
            data = (instrument_id, num_results)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return list(map(Order.from_tuple, cur.fetchall()))

    def get_best_sell_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price
                FROM TradeOrder
                JOIN Instrument ON TradeOrder.instrument_id = Instrument.id
                WHERE display_order = %s
                AND is_active
                AND side = 'sell'
                AND status = 'unfilled'
                ORDER BY price ASC, order_time ASC
                LIMIT '''
        if num_results == None:
            query += 'ALL'
            data = (display_order, )
        else:
            query += '%s'
            data = (display_order, num_results)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return list(map(Order.from_tuple, cur.fetchall()))

    def get_best_sell_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price
                FROM TradeOrder
                WHERE instrument_id = %s
                AND side = 'sell'
                AND status = 'unfilled'
                ORDER BY price ASC, order_time ASC
                LIMIT '''
        if num_results == None:
            query += 'ALL'
            data = (instrument_id, )
        else:
            query += '%s'
            data = (instrument_id, num_results)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return list(map(Order.from_tuple, cur.fetchall()))

    def update_order_status(self, order: Order, status: str) -> None:
        query = '''UPDATE TradeOrder
                SET status = %s
                FROM Instrument
                WHERE account_id = %s
                AND display_order = %s
                AND is_active
                AND side = %s
                AND status = 'unfilled' '''
        data = (status, order.account.id, order.instrument.display_order, str(order.side))

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
    
    def update_order_status_using(self, account_id: str, display_order: int, side: Side, status: str) -> None:
        query = '''UPDATE TradeOrder
                   SET status = %s
                   FROM Instrument
                   WHERE account_id = %s
                   AND display_order = %s
                   AND is_active
                   AND side = %s
                   AND status = 'unfilled' '''
        data = (status, account_id, display_order, side)

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
        data = (account_id, display_order, str(side))

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchone()
