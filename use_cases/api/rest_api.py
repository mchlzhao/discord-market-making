import json

from typing import List, Tuple

from entities.account import Account

from repos.account_repository import IAccountRepository
from repos.instrument_repository import IInstrumentRepository
from repos.position_repository import IPositionRepository

class ApiUseCase:
    def __init__(self, account_repository: IAccountRepository, instrument_repository: IInstrumentRepository,
            position_repository: IPositionRepository):

        self.account_repository: IAccountRepository = account_repository
        self.instrument_repository: IInstrumentRepository = instrument_repository
        self.position_repository: IPositionRepository = position_repository
    
    def get_account_info(self) -> dict:
        accounts: List[Account] = self.account_repository.get_all_accounts()
        response: dict = {'accounts': []}

        for account in accounts:
            positions: List[Tuple[int, int]] = self.position_repository.get_all_positions_by_account(account)

            response['accounts'].append({
                'id': account.id,
                'name': account.name,
                'balance': account.balance,
                'positions': positions
            })
        
        return response
