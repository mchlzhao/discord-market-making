from typing import List, Tuple

from entities.account import Account
from entities.instrument import Instrument

class IPositionRepository:
    def initialise_positions(self) -> None:
        raise NotImplementedError()

    def initialise_positions_of_account(self, account: Account) -> None:
        raise NotImplementedError()

    def update_account_position_in_instrument(self, account: Account, instrument: Instrument, inc: int) -> None:
        raise NotImplementedError()

    def get_account_position_in_instrument(self, account: Account, instrument: Instrument) -> int:
        raise NotImplementedError()

    def get_all_positions_in_instrument(self, instrument: Instrument) -> List[Tuple[str, int]]:
        raise NotImplementedError()
