import uuid
from datetime import datetime, timezone


class UsuarioEmpresa:
    def __init__(self, nome, username, email, senha, biografia="", tipo_usuario="empresa",
                 status_usuario="ativo", post_criados=None, eventos_criados=None,
                 seguidores=None, seguindo=None, foto_perfil="", cnpj="", setor=""):

        self.id = str(uuid.uuid4())
        self.nome = nome
        self.username = username
        self.email = email
        self.senha = senha
        self.biografia = biografia
        self.tipo_usuario = tipo_usuario
        self.status_usuario = status_usuario
        self.data_criacao = datetime.now(timezone.utc)
        self.post_criados = post_criados if post_criados is not None else []
        self.eventos_criados = eventos_criados if eventos_criados is not None else []
        self.seguidores = seguidores if seguidores is not None else []
        self.seguindo = seguindo if seguindo is not None else []
        self.foto_perfil = foto_perfil
        self.cnpj = cnpj
        self.setor = setor

    def to_dict(self):
        return {
            'id': self.id,
            "nome": self.nome,
            "username": self.username,
            "email": self.email,
            "senha": self.senha,
            "biografia": self.biografia,
            "tipo_usuario": self.tipo_usuario,
            "status_usuario": self.status_usuario,
            'data_criacao': self.data_criacao.isoformat(),
            "post_criados": self.post_criados,
            "eventos_criados": self.eventos_criados,
            "seguidores": self.seguidores,
            "seguindo": self.seguindo,
            "foto_perfil": self.foto_perfil,
            "cnpj": self.cnpj,
            "setor": self.setor
        }
