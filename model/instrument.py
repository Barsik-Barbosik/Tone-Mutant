class Instrument:
    def __init__(self, id: int, name: str, bank: int, program_change: int):
        self.id = id
        self.name = name
        self.bank = bank
        self.program_change = program_change

    def to_json(self):
        return {"id": self.id, "name": self.name}
