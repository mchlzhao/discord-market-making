class Instrument:
    def __init__(self, type_id: int, display_order: int, week_number: int, is_active: bool):
        self.type_id: int = type_id
        self.display_order: int = display_order
        self.week_number: int = week_number
        self.is_active: bool = is_active
    