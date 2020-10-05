from typing import List, Tuple

from entities.account import Account
from entities.instrument import Instrument

from repos.position_repository import IPositionRepository

class PostgresPositionRepository(IPositionRepository):
    def __init__(self, conn):
        self.conn = conn

    def initialise_positions(self) -> None:
        query = '''INSERT INTO Position (account_id, instrument_id, num_positions)
                   SELECT Account.id, Instrument.id, 0
                   FROM Account, Instrument
                   WHERE Instrument.is_active'''
        
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()
    
    def initialise_positions_of_account(self, account: Account):
        query = '''INSERT INTO Position (account_id, instrument_id, num_positions)
                   SELECT %s, id, 0
                   FROM Instrument
                   WHERE is_active'''
        data = (account.id, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def update_account_position_in_instrument(self, account: Account, instrument: Instrument, inc: int) -> None:
        query = '''UPDATE Position
                   SET num_positions = num_positions + %s
                   WHERE account_id = %s
                   AND instrument_id = %s'''
        data = (inc, account.id, instrument.id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def get_account_position_in_instrument(self, account: Account, instrument: Instrument) -> int:
        query = '''SELECT num_positions
                   FROM Position
                   WHERE account_id = %s
                   AND instrument_id = %s'''
        data = (account.id, instrument.id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        res = cur.fetchone()
        if res is None:
            return None

        return res[0]

    def get_all_positions_in_instrument(self, instrument: Instrument) -> List[Tuple[str, int]]:
        query = '''SELECT account_id, num_positions
                   FROM Position
                   JOIN Instrument on Position.instrument_id = Instrument.id
                   WHERE display_order = %s'''
        data = (instrument.display_order, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchall()

    def get_total_positions_in_active_instruments(self) -> List[Tuple[str, int]]:
        query = '''SELECT account_id, SUM(ABS(num_positions))
                   FROM Position
                   JOIN Instrument ON Position.instrument_id = Instrument.id
                   WHERE is_active
                   GROUP by account_id'''
        
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()

        return cur.fetchall()
