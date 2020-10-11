from typing import List

from entities.account import Account

class IAccountRepository:
    def add_account(self, account: Account) -> None:
        raise NotImplementedError()

    def get_all_accounts(self) -> List[Account]:
        raise NotImplementedError()

    def get_account_using_id(self, account_id: str) -> Account:
        raise NotImplementedError()

    def get_account_balance_using_id(self, account_id: str) -> int:
        raise NotImplementedError()

    def change_account_balance_using_id(self, account_id: str, new_balance: int) -> None:
        raise NotImplementedError()

    def increment_account_balance_using_id(self, account_id: str, inc: int) -> None:
        raise NotImplementedError()

    def save_weekly_balance(self, account_id: str, week_number: int) -> None:
        raise NotImplementedError()

    def save_bonus_amount(self, account_id: str, week_number: int, bonus: int) -> None:
        raise NotImplementedError()

    def get_weekly_balance(self, account_id: str, week_number: int) -> int:
        raise NotImplementedError()
