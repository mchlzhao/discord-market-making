import psycopg2

from datetime import datetime
from typing import List

from entities.order import Order
from entities.order_status import OrderStatus
from entities.side import Side

from repos.trading_repository import ITradingRepository

class PostgresTradingRepository(ITradingRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_order(self, order: Order) -> None:
        query = '''INSERT INTO TradeOrder (account_id, instrument_id, side, price, order_time, status, processed_time)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        data = (order.account_id, order.instrument_id, str(order.side), order.price, datetime.now(),
            str(order.status), None if order.status == OrderStatus.UNFILLED else datetime.now())

        cur = self.conn.cursor()
        cur.execute(query, data)

    def update_order_status_using_order(self, order: Order) -> None:
        query = '''UPDATE TradeOrder
                   SET status = %s, processed_time = %s
                   WHERE account_id = %s
                   AND instrument_id = %s
                   AND side = %s
                   AND status = 'unfilled' '''
        data = (str(order.status), None if order.status == OrderStatus.UNFILLED else datetime.now(),
            order.account_id, order.instrument_id, str(order.side))

        cur = self.conn.cursor()
        cur.execute(query, data)

    def get_order(self, account_id: str, instrument_id: int, side: Side) -> Order:
        query = '''SELECT account_id, instrument_id, side, price, status
                   FROM TradeOrder
                   WHERE status = 'unfilled'
                   AND account_id = %s
                   AND instrument_id = %s
                   AND side = %s'''
        data = (account_id, instrument_id, str(side))

        cur = self.conn.cursor()
        cur.execute(query, data)

        res = cur.fetchone()

        if res is None:
            return None

        return Order.from_tuple(res)
    
    def get_best_buy_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price, status
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

        return list(map(Order.from_tuple, cur.fetchall()))

    def get_best_buy_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price, status
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

        return list(map(Order.from_tuple, cur.fetchall()))

    def get_best_sell_using_display_order(self, display_order: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price, status
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

        return list(map(Order.from_tuple, cur.fetchall()))

    def get_best_sell_using_instrument_id(self, instrument_id: int, num_results: int = None) -> List[Order]:
        query = '''SELECT account_id, instrument_id, side, price, status
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

        return list(map(Order.from_tuple, cur.fetchall()))
