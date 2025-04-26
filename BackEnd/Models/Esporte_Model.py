import uuid

class Esporte:
    def __init__(self, nome, descricao):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.descricao = descricao

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao
        }
