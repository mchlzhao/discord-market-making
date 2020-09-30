from datetime import datetime
import psycopg2

from enum import IntEnum

class Side(IntEnum):
    BUY = 0
    SELL = 1

conn = psycopg2.connect(
    host = 'localhost',
    port = 5432,
    dbname = 'postgres',
    user = 'postgres',
    options='-c search_path="market_test"'
)

# account information

def add_account(account_id, name):
    query = '''INSERT INTO Account (id, name, balance)
               VALUES (%s, %s, 0)'''
    data = (account_id, name)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def get_account_balance(account_id):
    query = '''SELECT balance
               FROM Account
               WHERE id = %s'''
    data = (account_id, )

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchone()[0]

def change_account_balance(account_id, new_balance):
    query = '''UPDATE Account
               SET balance = %s
               WHERE id = %s'''
    data = (new_balance, account_id)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def increment_account_balance(account_id, inc):
    query = '''UPDATE Account
               SET balance = balance + %s
               WHERE id = %s'''
    data = (inc, account_id)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

# creating and updating instruments

def add_instrument_type(desc):
    query = '''INSERT INTO InstrumentType (description)
               VALUES (%s)'''
    data = (desc, )

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def add_instrument(type_id, display_order, week_number = None):
    if week_number == None:
        query = '''INSERT INTO Instrument (type_id, display_order, week_number, is_active)
                VALUES (%s, %s, NULL, TRUE)'''
        data = (type_id, display_order)
    else:
        query = '''INSERT INTO Instrument (type_id, display_order, week_number, is_active)
                VALUES (%s, %s, %s, TRUE)'''
        data = (type_id, display_order, week_number)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def instrument_deactivate_all():
    query = '''UPDATE Instrument
               SET is_active = FALSE'''
    
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def get_display_order_using_id(instrument_id):
    query = '''SELECT display_order
                FROM Instrument
                WHERE instrument_id = %s'''
    data = (instrument_id, )

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchone()[0]

# managing positions

def initialise_position():
    query = '''INSERT INTO Position (account_id, instrument_id, num_positions)
               SELECT Account.id, Instrument.id, 0
               FROM Account, Instrument
               WHERE Instrument.is_active'''
    
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()

def update_position_using_display_order(account_id, display_order, inc):
    query = '''UPDATE Position
               SET num_positions = num_positions + %s
               FROM Instrument
               WHERE Position.instrument_id = Instrument.id
               AND Instrument.is_active
               AND Instrument.display_order = %s
               AND Position.account_id = %s'''
    data = (inc, display_order, account_id)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def get_position(account_id, display_order):
    query = '''SELECT num_positions
               FROM Position
               JOIN Instrument
               ON Position.instrument_id = Instrument.id
               WHERE account_id = %s
               AND display_order = %s
               AND is_active'''
    data = (account_id, display_order)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchone()[0]

def get_all_positions_using_display_order(display_order):
    query = '''SELECT account_id, num_positions
               FROM Position
               JOIN Instrument on Position.instrument_id = Instrument.id
               WHERE display_order = %s'''
    data = (display_order, )

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchall()

# trading

def add_order_using_instrument_id(account_id, instrument_id, side, price, status):
    query = '''INSERT INTO TradeOrder (account_id, instrument_id, side, price, order_time, status)
               VALUES (%s, %s, %s, %s, %s, %s)'''
    data = (account_id, instrument_id, side, price, datetime.now(), status)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def add_order_using_display_order(account_id, display_order, side, price, status):
    query = '''INSERT INTO TradeOrder (account_id, side, price, order_time, status, instrument_id)
               SELECT %s, %s, %s, %s, %s, id
               FROM Instrument
               WHERE display_order = %s
               AND is_active'''
    data = (account_id, side, price, datetime.now(), status, display_order)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def get_best_buy_using_instrument_id(instrument_id, num_results = None):
    query = '''SELECT *
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

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchall()

def get_best_buy_using_display_order(display_order, num_results = None):
    query = '''SELECT *
               FROM TradeOrder
               WHERE instrument_id = 
                   (SELECT id
                   FROM Instrument
                   WHERE display_order = %s
                   AND is_active)
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
    
    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchall()

def get_best_sell_using_instrument_id(instrument_id, num_results = None):
    query = '''SELECT *
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

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchall()

def get_best_sell_using_display_order(display_order, num_results = None):
    query = '''SELECT *
               FROM TradeOrder
               WHERE instrument_id = 
                   (SELECT id
                   FROM Instrument
                   WHERE display_order = %s
                   AND is_active)
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
    
    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchall()

def update_order_status_using_instrument_id(account_id, instrument_id, side, status):
    query = '''UPDATE TradeOrder
               SET status = %s
               WHERE account_id = %s
               AND instrument_id = %s
               AND side = %s
               AND status = 'unfilled' '''
    data = (status, account_id, instrument_id, side)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def update_order_status_using_display_order(account_id, display_order, side, status):
    query = '''UPDATE TradeOrder
               SET status = %s
               FROM Instrument
               WHERE TradeOrder.instrument_id = Instrument.id
               AND display_order = %s
               AND is_active
               AND account_id = %s
               AND side = %s
               AND status = 'unfilled' '''
    data = (status, display_order, account_id, side)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

def get_existing_order(account_id, display_order, side):
    query = '''SELECT *
               FROM TradeOrder
               JOIN Instrument ON TradeOrder.instrument_id = Instrument.id
               WHERE status = 'unfilled'
               AND account_id = %s
               AND display_order = %s
               AND is_active
               AND side = %s'''
    data = (account_id, display_order, side)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()

    return cur.fetchone()

def add_transaction(buyer_id, seller_id, is_buyer_maker, instrument_id, price):
    query = '''INSERT INTO Transaction (transaction_time, buyer_id, seller_id, maker_side, instrument_id, price)
               VALUES (%s, %s, %s, %s, %s, %s)'''
    data = (datetime.now(), buyer_id, seller_id, 'buy' if is_buyer_maker else 'sell', instrument_id, price)

    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()