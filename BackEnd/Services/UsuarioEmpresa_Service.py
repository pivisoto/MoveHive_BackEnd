from datetime import date, datetime,  timedelta, timezone
from email import utils
import bcrypt
from firebase_admin import firestore, credentials, storage
from flask import g, jsonify
from utils.validar_cnpj import validar_cnpj
from Models.UsuarioEmpresa_Model import UsuarioEmpresa
from middlewares.generate_token import generate_token
from middlewares.auth_token import token_required
import firebase_admin
import logging
from firebase_admin import firestore
import smtplib
from utils import enviar_email
from Services.Notificacao_Service import criar_notificacao


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bucket = storage.bucket()
db = firestore.client()

# Implementado
def registrar_empresa(nome, username, email, senha, cnpj, setor="", biografia=""):
    empresas_ref = db.collection('UsuariosEmpresa')

    if list(empresas_ref.where('email', '==', email).limit(1).stream()):
        return {"erro": "E-mail já cadastrado"}

    if list(empresas_ref.where('username', '==', username).limit(1).stream()):
        return {"erro": "Username já cadastrado"}

    if list(empresas_ref.where('cnpj', '==', cnpj).limit(1).stream()):
        return {"erro": "CNPJ já cadastrado"}
    
    if not validar_cnpj(cnpj):
        return {"erro": "CNPJ inválido"}

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    empresa = UsuarioEmpresa(
        nome=nome,
        username=username,
        email=email,
        senha=senha_hash,
        biografia=biografia,
        tipo_usuario="empresa",
        status_usuario="ativo",
        cnpj=cnpj,
    )

    doc_ref = empresas_ref.document(empresa.id)
    doc_ref.set(empresa.to_dict())

    bucket = storage.bucket()
    blob = bucket.blob(f'UsuariosEmpresa/{empresa.id}/Fotos/.init')
    blob.upload_from_string('Pasta Fotos inicializada', content_type='text/plain')

    token = generate_token(doc_ref.id)

    return {"token": token}, 201


# Implementado
@token_required
def adicionar_dados_modal_empresa(dados_modal=None, arquivo_foto=None):
    empresa_id = g.user_id  
    doc_ref = db.collection('UsuariosEmpresa').document(empresa_id)

    if not doc_ref.get().exists:
        return {"erro": "Empresa não encontrada"}, 404

    dados_para_adicionar = {}

    if arquivo_foto:
        caminho = f"UsuariosEmpresa/{empresa_id}/Fotos/foto_perfil.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(arquivo_foto, content_type=arquivo_foto.content_type)
        blob.make_public()
        dados_para_adicionar['foto_perfil'] = blob.public_url

    if dados_modal:
        campos = ['biografia', 'setor']
        for campo in campos:
            if campo in dados_modal and dados_modal[campo]:
                dados_para_adicionar[campo] = dados_modal[campo]

    if dados_para_adicionar:
        doc_ref.update(dados_para_adicionar)

    return {
        "status": "sucesso",
        "mensagem": "Informações da empresa atualizadas com sucesso"
    }, 200


@token_required
def listar_empresas_sem_filtro():
    try:
        usuario_logado_id = g.user_id

        usuario_logado_ref = db.collection('Usuarios').document(usuario_logado_id)
        usuario_logado_doc = usuario_logado_ref.get()

        if not usuario_logado_doc.exists:
            usuario_logado_ref = db.collection('UsuariosEmpresa').document(usuario_logado_id)
            usuario_logado_doc = usuario_logado_ref.get()
            if not usuario_logado_doc.exists:
                return {'erro': 'Usuário autenticado não encontrado'}, 404


        lista_seguindo = usuario_logado_doc.to_dict().get('seguindo', [])

        todas_empresas_ref = db.collection('UsuariosEmpresa').stream()

        empresas_sugeridas = []
        for doc in todas_empresas_ref:
            if doc.id == usuario_logado_id:
                continue  
            
            if doc.id in lista_seguindo:
                continue  

            dados = doc.to_dict()

            empresas_sugeridas.append({
                'id': doc.id,
                'nome': dados.get('nome'),
                'username': dados.get('username'),
                'foto_perfil': dados.get('foto_perfil', ''),
                'biografia': dados.get('biografia', ''),
                'setor': dados.get('setor', ''),
                'seguidores': len(dados.get('seguidores', [])),
            })

        return {'empresas': empresas_sugeridas}, 200

    except Exception as e:
        print(f"Erro em listar_empresas: {e}")
        return {'erro': str(e)}, 500