import uuid
from datetime import datetime

class Postagem:
    def __init__(self, usuario_id, conteudo,  esporte_praticado,
                 imagem='', status_postagem='ativo',comentarios,contador_curtidas=0):
        
        self.id = str(uuid.uuid4())
        self.usuario_id = usuario_id
        self.conteudo = conteudo
        self.imagem = imagem
        self.data_criacao = datetime.utcnow()
        self.contador_curtidas = contador_curtidas
        self.status_postagem = status_postagem
        self.comentarios = comentarios
        self.esporte_praticado = esporte_praticado

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'conteudo': self.conteudo,
            'imagem': self.imagem,
            'data_criacao': self.data_criacao.isoformat(),
            'contador_curtidas': self.contador_curtidas,
            'status_postagem': self.status_postagem,
            'esporte_praticado': self.esporte_praticado
        }
