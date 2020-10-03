from enum import Enum

class Status(Enum):
    UNFILLED = 'unfilled'
    FILLED = 'filled'
    CANCELLED = 'cancelled'

    def __str__(self):
        return self.value
