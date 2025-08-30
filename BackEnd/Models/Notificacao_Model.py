import uuid
from datetime import datetime, timezone

class Notificacao:
    def __init__(self, usuario_destino_id, usuario_origem_id, tipo, referencia_id, mensagem, lida=False):
        self.id = str(uuid.uuid4())
        self.usuario_destino_id = usuario_destino_id
        self.usuario_origem_id = usuario_origem_id
        self.tipo = tipo 
        self.referencia_id = referencia_id  
        self.mensagem = mensagem
        self.lida = lida
        self.data_criacao = datetime.now(timezone.utc)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_destino_id': self.usuario_destino_id,
            'usuario_origem_id': self.usuario_origem_id,
            'tipo': self.tipo,
            'referencia_id': self.referencia_id,
            'mensagem': self.mensagem,
            'lida': self.lida,
            'data_criacao': self.data_criacao.isoformat()
        }
