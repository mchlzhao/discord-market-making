from entities.instrument_type import InstrumentType
from entities.instrument import Instrument

class InstrumentRepository():
    def add_instrument_type(self, instrument_type: InstrumentType) -> None:
        raise NotImplementedError()

    def add_instrument(self, instrument: Instrument) -> None:
        raise NotImplementedError()

    def deactivate_all(self) -> None:
        raise NotImplementedError()

    def get_display_order_using_id(self, instrument_id: int) -> int:
        raise NotImplementedError()
