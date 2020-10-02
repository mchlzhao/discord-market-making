import psycopg2

from entities.instrument_type import InstrumentType
from entities.instrument import Instrument
from repos.instrument_repository import InstrumentRepository

conn = psycopg2.connect(
    host = 'localhost',
    port = 5432,
    dbname = 'postgres',
    user = 'postgres',
    options='-c search_path="market_test"'
)

class PostgresInstrumentRepository(InstrumentRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_instrument_type(self, instrument_type: InstrumentType) -> None:
        query = '''INSERT INTO InstrumentType (description)
                VALUES (%s)'''
        data = (instrument_type.description, )

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

    def get_display_order_using_id(self, instrument_id: int) -> int:
        query = '''SELECT display_order
                    FROM Instrument
                    WHERE instrument_id = %s'''
        data = (instrument_id, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchone()[0]
