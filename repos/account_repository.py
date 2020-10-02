from entities.account import Account

class AccountRepository:
    def add_account(self, account: Account) -> None:
        raise NotImplementedError()

    def get_account_balance(self, account: Account) -> int:
        raise NotImplementedError()

    def change_account_balance(self, account: Account, new_balance: int) -> None:
        raise NotImplementedError()

    def increment_account_balance(self, account: Account, inc: int) -> None:
        raise NotImplementedError()
