import uuid

class Chat:
    def __init__(self, participantes=[], user_adm='', nome_chat='', ultima_mensagem='', horario_ultima_mensagem='',ultima_visualizacao_por_usuario=[],id_evento=""):
        self.id = str(uuid.uuid4())
        self.participantes = participantes 
        self.user_adm = user_adm
        self.nome_chat = nome_chat
        self.ultima_mensagem = ultima_mensagem 
        self.horario_ultima_mensagem = horario_ultima_mensagem
        self.ultima_visualizacao_por_usuario = ultima_visualizacao_por_usuario
        self.id_evento = id_evento

    def to_dict(self):
        return {
            'id': self.id,
            'participantes': self.participantes,
            'user_adm': self.user_adm,
            'nome_chat': self.nome_chat,
            'ultima_mensagem': self.ultima_mensagem,
            'horario_ultima_mensagem': self.horario_ultima_mensagem,
            'ultima_visualizacao_por_usuario': self.ultima_visualizacao_por_usuario,
            'id_evento': self.id_evento
        }
