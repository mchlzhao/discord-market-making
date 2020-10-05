from typing import Tuple

class Account:
    def __init__(self, id: str, name: str, balance: int):
        self.id: str = id
        self.name: str = name
        self.balance: int = balance
    
    @classmethod
    def from_tuple(cls, t: Tuple[str, str, int]):
        return cls(t[0], t[1], t[2])