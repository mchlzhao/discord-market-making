import psycopg2

from typing import List

from entities.instrument import Instrument
from entities.instrument_type import InstrumentType

from repos.instrument_repository import IInstrumentRepository

class PostgresInstrumentRepository(IInstrumentRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_instrument_type(self, description: str) -> None:
        query = '''INSERT INTO InstrumentType (description)
                   VALUES (%s)'''
        data = (description, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
    
    def get_instrument_type_by_similar_description(self, description: str) -> List[InstrumentType]:
        query = '''SELECT id, description
                   FROM InstrumentType
                   WHERE description LIKE %s'''
        data = ('%' + description + '%', )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return list(map(InstrumentType.from_tuple, cur.fetchall()))

    def add_instrument(self, instrument: Instrument) -> None:
        query = '''INSERT INTO Instrument (type_id, display_order, week_number, is_active, did_occur)
                   VALUES (%s, %s, %s, TRUE, %s)'''
        data = (instrument.type_id, instrument.display_order, instrument.week_number, instrument.did_occur)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
    
    def get_all_instruments(self) -> List[Instrument]:
        query = '''SELECT id, type_id, display_order, week_number, is_active, did_occur
                   FROM Instrument'''
        
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()

        return list(map(Instrument.from_tuple, cur.fetchall()))
    
    def update_instrument_did_occur(self, instrument: Instrument) -> None:
        query = '''UPDATE Instrument
                   SET did_occur = %s
                   WHERE id = %s'''
        data = (instrument.did_occur, instrument.id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def deactivate_all(self) -> None:
        query = '''UPDATE Instrument
                   SET is_active = FALSE'''
        
        cur = self.conn.cursor()
        cur.execute(query)
        self.conn.commit()

    def get_instrument_using_display_order(self, display_order: int) -> Instrument:
        query = '''SELECT id, type_id, display_order, week_number, is_active, did_occur
                   FROM Instrument
                   WHERE display_order = %s
                   AND is_active'''
        data = (display_order, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        res = cur.fetchone()

        if res is None:
            return None

        return Instrument.from_tuple(res)
