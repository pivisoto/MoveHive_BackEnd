import uuid
from datetime import datetime, timezone

class Evento:
    def __init__(self, usuario_id, titulo, descricao, esporte_nome, localizacao, endereco, data_hora,
                torneio=False, premiacao=0, foto=None, link_oficial=None, interesse=None, status=None):

        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.titulo = titulo
        self.descricao = descricao
        self.esporte_nome = esporte_nome
        self.localizacao = localizacao
        self.endereco = endereco
        self.data_hora = data_hora
        self.data_criacao = datetime.now(timezone.utc)
        self.torneio = torneio
        self.premiacao = premiacao if torneio else False
        self.foto = foto
        self.link_oficial = link_oficial
        self.interesse = interesse if interesse is not None else []
        self.status = status


    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'titulo': self.titulo,
            'descricao': self.descricao,
            'esporte_nome': self.esporte_nome,
            'localizacao': self.localizacao,
            'endereco': self.endereco,
            'data_hora': self.data_hora.isoformat() if isinstance(self.data_hora, datetime) else self.data_hora,
            'data_criacao': self.data_criacao.isoformat(),
            'torneio': self.torneio,
            'premiacao': self.premiacao,
            'foto': self.foto,
            'link_oficial': self.link_oficial,
            'interesse': self.interesse,
            'status': self.status
        }
