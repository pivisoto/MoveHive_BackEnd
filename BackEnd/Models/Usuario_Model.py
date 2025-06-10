import uuid
from datetime import datetime, timezone

class Usuario:
    def __init__(self, email, senha,    
                 data_nascimento, 
                 nome_completo,
                 username = "",
                 biografia='', 
                 foto_perfil='',
                 esportes_praticados=None,
                 estado =  "",
                 cidade = "",
                 tipo_usuario='comum', 
                 pontos = 0,
                 status_usuario='ativo',
                 post_criados = None,
                 eventos_criados=None, 
                 eventos_participando=None,
                 seguidores=None,
                 seguindo=None,
                 treinos_id=None):
        
        self.id = str(uuid.uuid4())
        self.nome_completo = nome_completo
        self.username = username
        self.email = email
        self.senha = senha
        self.biografia = biografia
        self.foto_perfil = foto_perfil
        self.estado = estado
        self.cidade = cidade
        self.data_nascimento = data_nascimento 
        self.data_criacao = datetime.now(timezone.utc)
        self.tipo_usuario = tipo_usuario
        self.pontos = pontos
        self.status_usuario = status_usuario
        self.post_criados = post_criados if post_criados is not None else []
        self.seguidores = seguidores if seguidores is not None else []
        self.seguindo = seguindo if seguindo is not None else []
        self.esportes_praticados = esportes_praticados if esportes_praticados is not None else {}
        self.eventos_criados = eventos_criados if eventos_criados is not None else []
        self.eventos_participando = eventos_participando if eventos_participando is not None else []
        self.treinos_id = treinos_id if treinos_id is not None else []


    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'username': self.username,
            'email': self.email,
            'senha': self.senha,
            'biografia': self.biografia,
            'foto_perfil': self.foto_perfil,
            'estado': self.estado,
            'cidade': self.cidade,
            'data_nascimento': self.data_nascimento.isoformat() if isinstance(self.data_nascimento, datetime) else self.data_nascimento,
            'data_criacao': self.data_criacao.isoformat(),
            'tipo_usuario': self.tipo_usuario,
            'pontos' : self.pontos,
            'status_usuario': self.status_usuario,
            'post_criados' : self.post_criados,
            'esportes_praticados': self.esportes_praticados,
            'eventos_criados': self.eventos_criados,
            'eventos_participando': self.eventos_participando,
            'seguidores': self.seguidores,
            'seguindo': self.seguindo,
            'treinos_id': self.treinos_id
        }
