import uuid
from datetime import datetime, timezone

class Evento:
    def __init__(self, usuario_id, titulo, descricao, esporte_nome, localizacao, data_hora,
                 max_participantes, torneio=False, premiacao=0, foto=None,
                 participantes=None, privado=False, observacoes=None):

        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.descricao = descricao
        self.esporte_nome = esporte_nome
        self.localizacao =  localizacao
        self.data_hora = data_hora
        self.max_participantes = max_participantes
        self.data_criacao = datetime.now(timezone.utc)
        self.torneio = torneio
        self.premiacao = premiacao if torneio else False 
        self.foto = foto  
        self.participantes = participantes if participantes is not None else []
        self.privado = privado
        self.observacoes = observacoes if observacoes else ""

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'esporte_nome': self.esporte_nome,
            'localizacao': self.localizacao,
            'data_hora': self.data_hora.isoformat() if isinstance(self.data_hora, datetime) else self.data_hora,
            'max_participantes': self.max_participantes,
            'data_criacao': self.data_criacao.isoformat(),
            'torneio': self.torneio,
            'premiacao': self.premiacao,
            'foto': self.foto,
            'participantes': self.participantes,
            'privado': self.privado,
            'observacoes': self.observacoes
        }
