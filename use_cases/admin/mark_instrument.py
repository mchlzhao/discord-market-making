from typing import List, Tuple

from entities.instrument import Instrument

from repos.account_repository import IAccountRepository
from repos.instrument_repository import IInstrumentRepository
from repos.position_repository import IPositionRepository

class MarkInstrumentUseCase:
    def __init__(self, account_repository: IAccountRepository, instrument_repository: IInstrumentRepository,
            position_repository: IPositionRepository):
        
        self.account_repository: IAccountRepository = account_repository
        self.instrument_repository: IInstrumentRepository = instrument_repository
        self.position_repository: IPositionRepository = position_repository
    
    def mark(self, display_order: int, did_occur: bool) -> int:
        instrument: Instrument = self.instrument_repository.get_instrument_using_display_order(display_order)
        if instrument is None:
            return -1
        
        positions: List[Tuple[str, int]] = self.position_repository.get_all_positions_in_instrument(instrument)

        if instrument.did_occur is not None:
            # previously marked with different outcome
            if instrument.did_occur:
                for account_id, position in positions:
                    self.account_repository.increment_account_balance_using_id(account_id, -100 * position)

        instrument.did_occur = did_occur
        self.instrument_repository.update_instrument_did_occur(instrument)

        if did_occur:
            positions: List[Tuple[str, int]] = self.position_repository.get_all_positions_in_instrument(instrument)

            for account_id, position in positions:
                self.account_repository.increment_account_balance_using_id(account_id, 100 * position)

        return 0
