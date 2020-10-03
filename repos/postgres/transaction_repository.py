from datetime import datetime

from entities.transaction import Transaction

from repos.transaction_repository import ITransactionRepository

class PostgresTransactionRepository(ITransactionRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_transaction(self, transaction: Transaction) -> None:
        query = '''INSERT INTO Transaction (transaction_time, buyer_id, seller_id, maker_side, instrument_id, price)
                SELECT %s, %s, %s, %s, id, %s
                FROM Instrument
                WHERE display_order = %s
                AND is_active'''
        data = (datetime.now(), transaction.buyer_account.id, transaction.seller_account.id,
            str(transaction.maker_side), transaction.price, transaction.instrument.display_order)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
