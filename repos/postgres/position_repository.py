from typing import List, Tuple

from entities.account import Account
from entities.instrument import Instrument
from repos.position_repository import PositionRepository

class PostgresPositionRepository(PositionRepository):
    def __init__(self, conn):
        self.conn = conn

    def initialise_position(self) -> None:
        query = '''INSERT INTO Position (account_id, instrument_id, num_positions)
                SELECT Account.id, Instrument.id, 0
                FROM Account, Instrument
                WHERE Instrument.is_active'''
        
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()

    def update_account_position_in_instrument(self, account: Account, instrument: Instrument, inc: int) -> None:
        query = '''UPDATE Position
                SET num_positions = num_positions + %s
                FROM Instrument
                WHERE Position.instrument_id = Instrument.id
                AND Instrument.is_active
                AND Instrument.display_order = %s
                AND Position.account_id = %s'''
        data = (inc, instrument.display_order, account.id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def get_account_position_in_instrument(self, account: Account, instrument: Instrument) -> int:
        query = '''SELECT num_positions
                FROM Position
                JOIN Instrument
                ON Position.instrument_id = Instrument.id
                WHERE account_id = %s
                AND display_order = %s
                AND is_active'''
        data = (account.id, instrument.display_order)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchone()[0]

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