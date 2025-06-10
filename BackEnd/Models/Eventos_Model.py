import uuid
from datetime import datetime, timezone

class Evento:
    def __init__(self, usuario_id, esporte_id, titulo, localizacao, data_hora,
                 descricao, max_participantes, nivel_esporte, visibilidade, evento_ativo=True, 
                 inscricoes_ativas=True,
                 participantes=None):
        
        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.descricao = descricao
        self.esporte_id = esporte_id
        self.nivel_esporte = nivel_esporte
        self.localizacao = localizacao if localizacao is not None else [] 
        self.data_hora = data_hora
        self.max_participantes = max_participantes
        self.data_criacao = datetime.now(timezone.utc)
        self.evento_ativo = evento_ativo
        self.visibilidade = visibilidade
        self.inscricoes_ativas = inscricoes_ativas
        self.participantes = participantes if participantes is not None else []



    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'esporte_id': self.esporte_id,
            'titulo': self.titulo,
            'localizacao': self.localizacao,
            'data_hora': self.data_hora.isoformat() if isinstance(self.data_hora, datetime) else self.data_hora,
            'data_criacao': self.data_criacao.isoformat(),
            'descricao': self.descricao,
            'max_participantes': self.max_participantes,
            'evento_ativo': self.evento_ativo,
            'nivel_esporte': self.nivel_esporte,
            'inscricoes_ativas': self.inscricoes_ativas,
            'participantes': self.participantes
        }
