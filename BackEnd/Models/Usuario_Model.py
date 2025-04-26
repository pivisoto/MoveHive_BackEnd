import uuid
from datetime import datetime

class Usuario:
    def __init__(self, email, senha, nome, estado, foto_perfil='', esporte_id='',
                 tipo_usuario='comum', status_usuario='ativo',
                 eventos_criados=None, eventos_participando=None):
        
        self.id = str(uuid.uuid4())
        self.email = email
        self.senha = senha
        self.nome = nome
        self.foto_perfil = foto_perfil
        self.estado = estado
        self.esporte_id = esporte_id
        self.data_criacao = datetime.utcnow()
        self.tipo_usuario = tipo_usuario
        self.status_usuario = status_usuario
        self.eventos_criados = eventos_criados if eventos_criados is not None else []
        self.eventos_participando = eventos_participando if eventos_participando is not None else []


    # Firebase (e muitas outras bibliotecas ou bancos) esperam os dados em formato de dicionário (dict) para salvar no banco.
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'senha': self.senha,
            'nome': self.nome,
            'foto_perfil': self.foto_perfil,
            'estado': self.estado,
            'esporte_id': self.esporte_id,
            'data_criacao': self.data_criacao.isoformat(),
            'tipo_usuario': self.tipo_usuario,
            'status_usuario': self.status_usuario,
            'eventos_criados': self.eventos_criados,
            'eventos_participando': self.eventos_participando
        }
