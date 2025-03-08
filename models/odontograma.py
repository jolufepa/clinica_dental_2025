import json

class Odontograma:
    def __init__(self, paciente_id, dientes=None):
        print(f"Constructor Odontograma llamado con paciente_id={paciente_id}, dientes={dientes}")
        self.paciente_id = paciente_id
        self.dientes = dientes if dientes is not None else {i: {"estado": "sano", "notas": ""} for i in range(1, 33)}

    def to_dict(self):
        return {
            "paciente_id": self.paciente_id,
            "dientes": self.dientes
        }

    @classmethod
    def from_dict(cls, data):
        paciente_id = data.get("paciente_id")
        dientes = data.get("dientes")
        if dientes is None:
            dientes = {i: {"estado": "sano", "notas": ""} for i in range(1, 33)}
        print(f"from_dict: paciente_id={paciente_id}, dientes={dientes}")
        return cls(paciente_id, dientes)