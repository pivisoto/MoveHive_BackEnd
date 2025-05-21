import bcrypt
from firebase_admin import firestore, credentials
from flask import g, jsonify
from Models.Usuario_Model import Usuario
from middlewares.token_required import generate_token
from middlewares.auth_token import token_required
import firebase_admin


if not firebase_admin._apps:
    cred = credentials.Certificate("move-hive-firebase-adminsdk-fbsvc-0334323fd4.json")
    firebase_admin.initialize_app(cred)



db = firestore.client()


# Função para Registar Usuario
def registrar_usuario(nome_completo, username, email, senha, estado, cidade, esportes_praticados,seguidores,seguindo):
    usuarios_ref = db.collection('Usuarios')

    # Verifica se o e-mail já está cadastrado
    email_query = usuarios_ref.where('email', '==', email).limit(1)
    email_docs = list(email_query.stream())
    if email_docs:
        return {"erro": "E-mail já cadastrado"}, 400

    # Verifica se o username já está cadastrado
    username_query = usuarios_ref.where('username', '==', username).limit(1)
    username_docs = list(username_query.stream())
    if username_docs:
        return {"erro": "Username já está em uso"}, 400

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    usuario = Usuario(
        nome_completo=nome_completo,
        username=username,
        email=email,
        senha=senha_hash,
        estado=estado,
        cidade=cidade,
        esportes_praticados=esportes_praticados,
        seguidores=seguidores,
        seguindo=seguindo
    )

    doc_ref = usuarios_ref.document(usuario.id)
    doc_ref.set(usuario.to_dict())

    return {"status": "sucesso", "id": doc_ref.id}, 201


# Função para Logar Usuario
def login_usuario(email, senha):
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('email', '==', email).limit(1)
    docs = query.stream()
    usuario_doc = next(docs, None)

    if not usuario_doc:
        return {"erro": "E-mail não encontrado"}, 400

    dados = usuario_doc.to_dict()
    if not bcrypt.checkpw(senha.encode('utf-8'), dados['senha'].encode('utf-8')):
        return {"erro": "Senha incorreta"}, 400
    
    token = generate_token(usuario_doc.id)

    resposta = {
        "status": "sucesso",
        "mensagem": "Login bem-sucedido",
        "token": token,
    }
    
    return resposta, 200



# Função para Listar Usuarios
@token_required  
def listar_usuarios():
    usuarios = db.collection('Usuarios').stream()
    lista = []
    for doc in usuarios:
        dados = doc.to_dict()
        dados['id'] = doc.id  
        lista.append(dados)   
    return lista


# Função para Deletar Usuario por ID
@token_required  
def deletar_usuario_por_id(usuario_id):
    doc_ref = db.collection('Usuarios').document(usuario_id)
    if not doc_ref.get().exists:
        return {"erro": "Usuário não encontrado"}, 404

    doc_ref.delete()
    return {"status": "sucesso", "mensagem": "Usuário deletado com sucesso"}, 200



# Função para Editar Usuario por ID
def editar_usuario_por_id(novos_dados):
    usuario_id = g.user_id
    doc_ref = db.collection('Usuarios').document(usuario_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return {"erro": "Usuário não encontrado"}, 404

    dados_atualizados = novos_dados.copy()

    if 'senha' in novos_dados:
        dados_atualizados['senha'] = bcrypt.hashpw(novos_dados['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    doc_ref.update(dados_atualizados)
    return {"status": "sucesso", "mensagem": "Usuário atualizado com sucesso"}, 200


def toggle_seguir_usuario(solicitacao):
    usuario_pedindo = g.user_id
    usuario_seguido = solicitacao['id_solicitando']

    doc_ref_solicitante = db.collection('Usuarios').document(usuario_pedindo)
    doc_ref_seguido = db.collection('Usuarios').document(usuario_seguido)

    snapshot_solicitante = doc_ref_solicitante.get()
    snapshot_seguido = doc_ref_seguido.get()

    if not snapshot_solicitante.exists:
        return {"erro": "Usuário solicitante não encontrado"}, 404

    if not snapshot_seguido.exists:
        return {"erro": "Usuário seguido não encontrado"}, 404

    dados_solicitante = snapshot_solicitante.to_dict()
    dados_seguido = snapshot_seguido.to_dict()
    seguindo_solicitante = dados_solicitante.get('seguindo', [])
    seguidores_seguido = dados_seguido.get('seguidores', [])

    if usuario_seguido in seguindo_solicitante:
        seguindo_solicitante.remove(usuario_seguido)
        seguidores_seguido.remove(usuario_pedindo)
        doc_ref_solicitante.update({"seguindo": seguindo_solicitante})
        doc_ref_seguido.update({"seguidores": seguidores_seguido})
        return {"status": "sucesso", "mensagem": "Você deixou de seguir o usuário"}, 201
    else:
        seguindo_solicitante.append(usuario_seguido)
        seguidores_seguido.append(usuario_pedindo)
        doc_ref_solicitante.update({"seguindo": seguindo_solicitante})
        doc_ref_seguido.update({"seguidores": seguidores_seguido})
        return {"status": "sucesso", "mensagem": "Você começou a seguir o usuário"}, 200

  
def buscar_usuario_por_id(user_id):
    usuario_ref = db.collection('Usuarios').document(user_id)
    usuario = usuario_ref.get()

    if not usuario.exists:
        return jsonify({'erro': 'Usuário não encontrado!'}), 404

    return usuario.to_dict()
