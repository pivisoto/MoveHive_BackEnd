import uuid
from datetime import datetime

class Evento:
    def __init__(self, usuario_id, esporte_id, nome, localizacao, data_hora,
                 descricao, max_participantes, nivel_esporte, status_evento='Ativo', link_oficial='',
                 tipo_evento='',  inscricoes_ativas=True,
                 participantes=None):
        
        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.esporte_id = esporte_id
        self.nome = nome
        self.localizacao = localizacao
        self.data_hora = data_hora
        self.data_criacao = datetime.utcnow()
        self.descricao = descricao
        self.max_participantes = max_participantes
        self.status_evento = status_evento
        self.link_oficial = link_oficial
        self.tipo_evento = tipo_evento
        self.nivel_esporte = nivel_esporte
        self.inscricoes_ativas = inscricoes_ativas
        self.participantes = participantes if participantes is not None else []



    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'esporte_id': self.esporte_id,
            'nome': self.nome,
            'localizacao': self.localizacao,
            'data_hora': self.data_hora.isoformat() if isinstance(self.data_hora, datetime) else self.data_hora,
            'data_criacao': self.data_criacao.isoformat(),
            'descricao': self.descricao,
            'max_participantes': self.max_participantes,
            'status_evento': self.status_evento,
            'link_oficial': self.link_oficial,
            'tipo_evento': self.tipo_evento,
            'nivel_esporte': self.nivel_esporte,
            'inscricoes_ativas': self.inscricoes_ativas,
            'participantes': self.participantes
        }
