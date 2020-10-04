from typing import Tuple

class InstrumentType:
    def __init__(self, id: int, description: str):
        self.id: int = id
        self.description: str = description
    
    @classmethod
    def from_tuple(cls, t: Tuple[int, str]):
        return cls(t[0], t[1])
