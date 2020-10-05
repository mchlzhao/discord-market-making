from entities.account import Account

from repos.account_repository import IAccountRepository
from repos.position_repository import IPositionRepository

class AddAccountUseCase:
    def __init__(self, account_repository: IAccountRepository, position_repository: IPositionRepository):
        self.account_repository: IAccountRepository = account_repository
        self.position_repository: IPositionRepository = position_repository
    
    def add_account(self, account_id: str, name: str, balance: int) -> int:
        account: Account = Account(account_id, name, balance)

        existing: Account = self.account_repository.get_account_using_id(account_id)
        if existing is not None:
            return -1

        self.account_repository.add_account(account)
        self.position_repository.initialise_positions_of_account(account)

        return 0
