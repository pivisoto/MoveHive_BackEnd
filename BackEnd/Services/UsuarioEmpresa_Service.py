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

