import psycopg2

from entities.instrument_type import InstrumentType
from entities.instrument import Instrument
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

    def add_instrument(self, instrument: Instrument) -> None:
        if instrument.week_number == None:
            query = '''INSERT INTO Instrument (type_id, display_order, week_number, is_active)
                    VALUES (%s, %s, NULL, TRUE)'''
            data = (instrument.type_id, instrument.display_order)
        else:
            query = '''INSERT INTO Instrument (type_id, display_order, week_number, is_active)
                    VALUES (%s, %s, %s, TRUE)'''
            data = (instrument.type_id, instrument.display_order, instrument.week_number)

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
        query = '''SELECT type_id, display_order, week_number, is_active
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

        return Instrument(res[0], res[1], res[2], res[3])