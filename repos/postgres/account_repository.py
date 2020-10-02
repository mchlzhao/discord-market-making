import psycopg2

from entities.account import Account
from repos.account_repository import AccountRepository

conn = psycopg2.connect(
    host = 'localhost',
    port = 5432,
    dbname = 'postgres',
    user = 'postgres',
    options='-c search_path="market_test"'
)

class PostgresAccountRepository(AccountRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_account(self, account: Account) -> None:
        query = '''INSERT INTO Account (id, name, balance)
                VALUES (%s, %s, 0)'''
        data = (account.id, account.name)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def get_account_balance(self, account: Account) -> int:
        query = '''SELECT balance
                FROM Account
                WHERE id = %s'''
        data = (account.id, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        return cur.fetchone()[0]

    def change_account_balance(self, account: Account, new_balance: int) -> None:
        query = '''UPDATE Account
                SET balance = %s
                WHERE id = %s'''
        data = (new_balance, account.id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def increment_account_balance(self, account: Account, inc: int) -> None:
        query = '''UPDATE Account
                SET balance = balance + %s
                WHERE id = %s'''
        data = (inc, account.id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
