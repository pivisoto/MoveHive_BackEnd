import uuid

class Chat:
    def __init__(self, participantes=[], user_adm='', nome_chat='', ultima_mensagem='', horario_ultima_mensagem='', lida=False):
        self.id = str(uuid.uuid4())
        self.participantes = participantes 
        self.user_adm = user_adm
        self.nome_chat = nome_chat
        self.ultima_mensagem = ultima_mensagem 
        self.horario_ultima_mensagem = horario_ultima_mensagem

    def to_dict(self):
        return {
            'id': self.id,
            'participantes': self.participantes,
            'user_adm': self.user_adm,
            'nome_chat': self.nome_chat,
            'ultima_mensagem': self.ultima_mensagem,
            'horario_ultima_mensagem': self.horario_ultima_mensagem
        }
