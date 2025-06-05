import uuid

class Esporte:
    def __init__(self, nome, descricao, Kcal_por_1hr):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.descricao = descricao
        self.Kcal_por_1hr = Kcal_por_1hr

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'Kcal_por_1hr' : self.Kcal_por_1hr
        }
