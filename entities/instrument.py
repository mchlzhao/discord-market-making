from typing import Tuple

class Instrument:
    def __init__(self, id: int, type_id: int, display_order: int, week_number: int, is_active: bool):
        self.id: int = id
        self.type_id: int = type_id
        self.display_order: int = display_order
        self.week_number: int = week_number
        self.is_active: bool = is_active
    
    @classmethod
    def from_tuple(cls, t: Tuple[int, int, int, int, bool]):
        return cls(t[0], t[1], t[2], t[3], t[4])
