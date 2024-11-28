class Instrument:
    def __init__(self, id: int, name: str, bank: int, program: int):
        self.id = id
        self.name = name
        self.bank = bank
        self.program = program

    def to_json(self):
        return {"id": self.id, "name": self.name, "bank": self.bank, "program": self.program}
