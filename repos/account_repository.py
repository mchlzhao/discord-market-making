from entities.account import Account

class IAccountRepository:
    def add_account(self, account: Account) -> None:
        raise NotImplementedError()

    def get_account_balance_using_id(self, account_id: str) -> int:
        raise NotImplementedError()

    def change_account_balance_using_id(self, account_id: str, new_balance: int) -> None:
        raise NotImplementedError()

    def increment_account_balance_using_id(self, account_id: str, inc: int) -> None:
        raise NotImplementedError()

    def get_account_using_id(self, account_id: str) -> Account:
        raise NotImplementedError()
