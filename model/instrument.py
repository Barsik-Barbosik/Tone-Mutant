class Instrument:
    def __init__(self, id: int, name: str, program_change: int, bank: int):
        self.id = id
        self.name = name
        self.program_change = program_change
        self.bank = bank

    def to_json(self):
        return {"id": self.id, "name": self.name}
