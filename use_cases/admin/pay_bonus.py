from typing import List, Tuple

from repos.account_repository import IAccountRepository
from repos.position_repository import IPositionRepository

import settings

class PayBonusUseCase:
    POSITION_MULTIPLIER = 5

    def __init__(self, account_repository: IAccountRepository, position_repository: IPositionRepository):
        self.account_repository: IAccountRepository = account_repository
        self.position_repository: IPositionRepository = position_repository
    
    def pay_bonus(self) -> dict:
        total_positions: List[Tuple[str, int]] = self.position_repository.get_total_positions_in_active_instruments()

        bonus_amounts: dict = {}

        for account_id, total in total_positions:
            bonus_amount: int = total * self.POSITION_MULTIPLIER
            self.account_repository.increment_account_balance_using_id(account_id, bonus_amount)
            self.account_repository.save_bonus_amount(account_id, settings.WEEK_NUMBER, bonus_amount)

            bonus_amounts[account_id] = bonus_amount
        
        return bonus_amounts