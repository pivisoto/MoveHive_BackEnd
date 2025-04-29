import uuid
from datetime import datetime

class Comentario:
    def __init__(self, usuario_id, postagem_id, conteudo, status_comentario='ativo'):
        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.postagem_id = postagem_id
        self.conteudo = conteudo
        self.data_criacao = datetime.utcnow()
        self.status_comentario = status_comentario

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'postagem_id': self.postagem_id,
            'conteudo': self.conteudo,
            'data_criacao': self.data_criacao.isoformat(),
            'status_comentario': self.status_comentario
        }