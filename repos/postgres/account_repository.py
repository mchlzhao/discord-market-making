import psycopg2
from typing import List

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
    
    def get_all_accounts(self) -> List[Account]:
        query = '''SELECT id, name, balance
                   FROM Account'''
        
        cur = self.conn.cursor()
        cur.execute(query)

        return list(map(Account.from_tuple, cur.fetchall()))

    def get_account_using_id(self, account_id: str) -> Account:
        query = '''SELECT id, name, balance
                   FROM Account
                   WHERE id = %s'''
        data = (account_id, )

        cur = self.conn.cursor()
        cur.execute(query, data)

        res = cur.fetchone()
        
        if res is None:
            return None

        return Account.from_tuple(res)

    def get_account_balance_using_id(self, account_id: str) -> int:
        query = '''SELECT balance
                   FROM Account
                   WHERE id = %s'''
        data = (account_id, )

        cur = self.conn.cursor()
        cur.execute(query, data)

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

    def increment_account_balance_using_id(self, account_id: str, inc: int) -> None:
        query = '''UPDATE Account
                   SET balance = balance + %s
                   WHERE id = %s'''
        data = (inc, account_id)

        cur = self.conn.cursor()
        cur.execute(query, data)

    def save_weekly_balance(self, account_id: str, week_number: int) -> None:
        query = '''INSERT INTO WeeklyBalance (account_id, week_number, balance)
                   SELECT id, %s, balance
                   FROM Account
                   WHERE id = %s'''
        data = (week_number, account_id)

        cur = self.conn.cursor()
        cur.execute(query, data)

    def save_bonus_amount(self, account_id: str, week_number: int, bonus: int) -> None:
        query = '''INSERT INTO BonusAmount (account_id, week_number, bonus)
                   VALUES (%s, %s ,%s)'''
        data = (account_id, week_number, bonus)

        cur = self.conn.cursor()
        cur.execute(query, data)

    def get_weekly_balance(self, account_id: str, week_number: int) -> int:
        query = '''SELECT balance
                   FROM WeeklyBalance
                   WHERE account_id = %s
                   AND week_number = %s'''
        data = (account_id, week_number)

        cur = self.conn.cursor()
        cur.execute(query, data)

        res = cur.fetchone()
        if res is None:
            return None

        return res[0]
