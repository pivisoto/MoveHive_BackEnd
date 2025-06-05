import uuid
from datetime import datetime

class Treinos:
    def __init__(self, usuario_id, titulo, descricao, esporte, data_hora, lugar, tempo_treinado, arquivo_imagem=""):
        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.descricao = descricao
        self.esporte = esporte  
        self.data_hora = data_hora  
        self.lugar = lugar
        self.tempo_treinado = tempo_treinado  
        self.arquivo_imagem = arquivo_imagem
        self.pontos = self.calcular_pontos()

    def calcular_pontos(self):
        kcal_por_hora = self.esporte.Kcal_por_1hr if hasattr(self.esporte, 'Kcal_por_1hr') else self.esporte.get('Kcal_por_1hr', 0)
        return round((kcal_por_hora / 60) * self.tempo_treinado, 2)  

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'esporte': {
                'id': self.esporte.id if hasattr(self.esporte, 'id') else self.esporte.get('id'),
                'nome': self.esporte.nome if hasattr(self.esporte, 'nome') else self.esporte.get('nome'),
                'descricao': self.esporte.descricao if hasattr(self.esporte, 'descricao') else self.esporte.get('descricao'),
                'Kcal_por_1hr': self.esporte.Kcal_por_1hr if hasattr(self.esporte, 'Kcal_por_1hr') else self.esporte.get('Kcal_por_1hr')
            },
            'data_hora': self.data_hora.isoformat() if isinstance(self.data_hora, datetime) else self.data_hora,
            'lugar': self.lugar,
            'tempo_treinado': self.tempo_treinado,
            'pontos': self.pontos,
            'arquivo_imagem': self.arquivo_imagem
        }
