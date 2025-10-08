import uuid
from datetime import datetime, timezone

class Postagem:
    def __init__(self, usuario_id, descricao, 
                 imagem='', status_postagem='ativo', comentarios=None, contador_curtidas=0,curtidas=[]):
        
        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.descricao = descricao
        self.imagem = imagem
        self.data_criacao = datetime.now(timezone.utc)
        self.contador_curtidas = contador_curtidas
        self.curtidas = curtidas
        self.status_postagem = status_postagem
        self.comentarios = comentarios if comentarios is not None else []


    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'descricao': self.descricao,
            'imagem': self.imagem,
            'data_criacao': self.data_criacao.isoformat(),
            'contador_curtidas': self.contador_curtidas,
            'curtidas': self.curtidas,
            'status_postagem': self.status_postagem,
            'comentarios' : self.comentarios
        }
