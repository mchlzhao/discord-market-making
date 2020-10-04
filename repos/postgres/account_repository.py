import psycopg2

from entities.account import Account

from repos.account_repository import IAccountRepository

class PostgresAccountRepository(IAccountRepository):
    def __init__(self, conn):
        self.conn = conn

    def add_account(self, account: Account) -> None:
        query = '''INSERT INTO Account (id, name, balance)
                VALUES (%s, %s, %s)'''
        data = (account.id, account.name, account.balance)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def get_account_using_id(self, account_id: str) -> Account:
        query = '''SELECT name, balance
                    FROM Account
                    WHERE id = %s'''
        data = (account_id, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        res = cur.fetchone()
        
        if res is None:
            return None

        return Account(account_id, res[0], res[1])

    def get_account_balance_using_id(self, account_id: str) -> int:
        query = '''SELECT balance
                FROM Account
                WHERE id = %s'''
        data = (account_id, )

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

        res = cur.fetchone()
        
        if res is None:
            return None

        return res[0]

    def change_account_balance_using_id(self, account_id: str, new_balance: int) -> None:
        query = '''UPDATE Account
                SET balance = %s
                WHERE id = %s'''
        data = (new_balance, account_id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()

    def increment_account_balance_using_id(self, account_id: str, inc: int) -> None:
        query = '''UPDATE Account
                SET balance = balance + %s
                WHERE id = %s'''
        data = (inc, account_id)

        cur = self.conn.cursor()
        cur.execute(query, data)
        self.conn.commit()
