from enum import Enum

class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'

    def __str__(self):
        return self.value
