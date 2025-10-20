from datetime import date, datetime,  timedelta, timezone
from email import utils
import time
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

    token = generate_token(doc_ref.id, tipo_usuario="empresa")

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


# Implementado
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
    

# Implementado
@token_required
def meuPerfilEmpresa():
    try:
        usuario_id = g.user_id

        usuario_ref = db.collection('UsuariosEmpresa').document(usuario_id)
        usuario_doc = usuario_ref.get()

        if not usuario_doc.exists:
            return jsonify({'erro': 'Usuário empresa não encontrado!'}), 404

        usuario_data = usuario_doc.to_dict()

        total_posts = len(usuario_data.get('post_criados', []))
        total_eventos = len(usuario_data.get('eventos_criados', []))

        total_seguidores = len(usuario_data.get('seguidores', []))
        total_seguindo = len(usuario_data.get('seguindo', []))

        # Adicionar métricas ao dicionário de resposta
        usuario_data['total_posts'] = total_posts
        usuario_data['total_eventos'] = total_eventos
        usuario_data['seguidores_count'] = total_seguidores
        usuario_data['seguindo_count'] = total_seguindo

        # Remover dados sensíveis e listas completas
        usuario_data.pop('senha', None)
        usuario_data.pop('seguidores', None)
        usuario_data.pop('seguindo', None)
        usuario_data.pop('post_criados', None)
        usuario_data.pop('eventos_criados', None)

        return usuario_data, 200

    except Exception as e:
        print(f"Erro ao buscar perfil da empresa {g.user_id}: {e}")
        return jsonify({'erro': 'Ocorreu um erro interno ao processar o perfil da empresa.'}), 500



@token_required
def editar_empresa(dados, foto_perfil=None):
    usuario_id = g.user_id
    usuario_ref = db.collection('UsuariosEmpresa').document(usuario_id)

    try:
        usuario_doc = usuario_ref.get()
        if not usuario_doc.exists:
            return {"erro": "Usuário empresa não encontrado."}, 404
    except Exception as e:
        return {"erro": f"Erro ao acessar o banco de dados: {str(e)}"}, 500

    updates = {}

    for campo, valor in dados.items():
        if valor is None or valor == '':
            continue

        try:
            if campo == 'username':
                empresas_com_mesmo_username = db.collection('UsuariosEmpresa').where('username', '==', valor).limit(1).get()
                if len(empresas_com_mesmo_username) > 0 and empresas_com_mesmo_username[0].id != usuario_id:
                    return {"erro": f"O username '{valor}' já está em uso."}, 409
                updates[campo] = valor

            elif campo == 'email':
                empresas_com_mesmo_email = db.collection('UsuariosEmpresa').where('email', '==', valor).limit(1).get()
                if len(empresas_com_mesmo_email) > 0 and empresas_com_mesmo_email[0].id != usuario_id:
                    return {"erro": f"O email '{valor}' já está em uso."}, 409
                updates[campo] = valor

            elif campo == 'senha':
                senha_hash = bcrypt.hashpw(valor.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                updates[campo] = senha_hash

            elif campo in ['nome', 'biografia', 'setor']:
                updates[campo] = str(valor)

            elif campo == 'cnpj':
                validar_cnpj(campo)
                updates[campo] = str(valor)

        except Exception as e:
            return {"erro": f"Ocorreu um erro ao processar o campo '{campo}': {str(e)}"}, 500

    # Upload da foto de perfil
    if foto_perfil:
        try:
            caminho = f"UsuariosEmpresa/{usuario_id}/Fotos/foto_perfil.jpg"
            blob = bucket.blob(caminho)
            foto_perfil.seek(0)
            blob.upload_from_file(foto_perfil, content_type=foto_perfil.content_type)
            blob.make_public()
            timestamp = int(time.time())
            updates['foto_perfil'] = f"{blob.public_url}?v={timestamp}"
        except Exception as e:
            return {"erro": f"Erro ao fazer upload da imagem: {str(e)}"}, 500

    if not updates:
        return {"mensagem": "Nenhuma alteração foi feita."}, 200

    try:
        usuario_ref.update(updates)
        return {"mensagem": "Usuário empresa atualizado com sucesso."}, 200
    except Exception as e:
        return {"erro": f"Erro ao atualizar o usuário empresa no banco de dados: {str(e)}"}, 500
