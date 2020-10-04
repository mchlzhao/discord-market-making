from typing import List

from entities.instrument import Instrument
from entities.instrument_type import InstrumentType

class IInstrumentRepository():
    def add_instrument_type(self, instrument_type: InstrumentType) -> None:
        raise NotImplementedError()

    def get_instrument_type_by_similar_description(self, description: str) -> List[InstrumentType]:
        raise NotImplementedError()

    def add_instrument(self, instrument: Instrument) -> None:
        raise NotImplementedError()

    def deactivate_all(self) -> None:
        raise NotImplementedError()

    def get_display_order_using_id(self, instrument_id: int) -> int:
        raise NotImplementedError()

    def get_instrument_using_display_order(self, display_order: int) -> Instrument:
        raise NotImplementedError()
