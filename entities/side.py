from enum import IntEnum

class Side(IntEnum):
    BUY = 0
    SELL = 1

    def __str__(self):
        return str(self.name).lower()