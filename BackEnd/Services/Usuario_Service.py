from datetime import date, datetime
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


def calcular_idade(data_nascimento):
    hoje = date.today()
    idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
    return idade




# Função para Registar Usuario
def registrar_usuario(username, data_nascimento_str, email, senha):
    usuarios_ref = db.collection('Usuarios')

    if list(usuarios_ref.where('email', '==', email).limit(1).stream()):
        return {"erro": "E-mail já cadastrado"}

    if list(usuarios_ref.where('username', '==', username).limit(1).stream()):
        return {"erro": "Username já está em uso"}

    try:
        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
    except ValueError:
        return {"erro": "Data de nascimento inválida. Use o formato YYYY-MM-DD."}

    if data_nascimento > date.today():
        return {"erro": "Data de nascimento não pode ser futura."}

    if data_nascimento.year < 1900:
        return {"erro": "Ano de nascimento inválido."}

    idade = calcular_idade(data_nascimento)
    if idade < 18:
        return {"erro": "É necessário ter pelo menos 18 anos para se cadastrar."}

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    usuario = Usuario(
        username=username,
        email=email,
        senha=senha_hash,
        data_nascimento=data_nascimento_str
    )

    doc_ref = usuarios_ref.document(usuario.id)
    doc_ref.set(usuario.to_dict())

    token = generate_token(doc_ref.id)

    return {"token": token}, 201



# Função para Logar Usuario
def login_usuario(email, senha):
    usuarios_ref = db.collection('Usuarios')
    docs = usuarios_ref.where('email', '==', email).limit(1).stream()
    usuario_doc = next(docs, None)

    if not usuario_doc:
        return {"erro": "E-mail não encontrado"}

    dados = usuario_doc.to_dict()
    if not bcrypt.checkpw(senha.encode('utf-8'), dados['senha'].encode('utf-8')):
        return {"erro": "Senha incorreta"}

    token = generate_token(usuario_doc.id)

    return {"token": token}, 200



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
    usuario_pedindo_id = '24873626-9b10-480e-b8e6-6cf661eebb6e'
    username_seguido = solicitacao['username']

    doc_ref_solicitante = db.collection('Usuarios').document(usuario_pedindo_id)
    snapshot_solicitante = doc_ref_solicitante.get()

    if not snapshot_solicitante.exists:
        return {"erro": "Usuário solicitante não encontrado"}, 404

    dados_solicitante = snapshot_solicitante.to_dict()
    username_solicitante = dados_solicitante.get('username')

    if not username_solicitante:
        return {"erro": "Username do solicitante não encontrado"}, 400

    usuarios_ref = db.collection('Usuarios')
    query_seguido = usuarios_ref.where('username', '==', username_seguido).limit(1)
    resultado_seguido = list(query_seguido.stream())

    if not resultado_seguido:
        return {"erro": "Usuário a ser seguido não encontrado"}, 404

    doc_snapshot_seguido = resultado_seguido[0]
    doc_ref_seguido = doc_snapshot_seguido.reference
    dados_seguido = doc_snapshot_seguido.to_dict()

    seguindo_solicitante = dados_solicitante.get('seguindo', [])
    seguidores_seguido = dados_seguido.get('seguidores', [])

    if username_seguido in seguindo_solicitante:
        seguindo_solicitante.remove(username_seguido)
        seguidores_seguido.remove(username_solicitante)
        mensagem = "Você deixou de seguir o usuário"
        status_code = 201
    else:
        seguindo_solicitante.append(username_seguido)
        seguidores_seguido.append(username_solicitante)
        mensagem = "Você começou a seguir o usuário"
        status_code = 200

    doc_ref_solicitante.update({"seguindo": seguindo_solicitante})
    doc_ref_seguido.update({"seguidores": seguidores_seguido})
    return {"status": "sucesso", "mensagem": "Lista de seguidores e seguindo atualizadas com sucesso"}, 200 


def listar_seguindo(username):
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('username', '==', username).limit(1)
    resultados = query.stream()
    for doc in resultados:
        dados_usuario = doc.to_dict()
        seguindo = dados_usuario.get('seguindo', [])
        return seguindo
    return {"erro": "Usuário não encontrado"}, 404
     

def listar_seguidores(username):
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('username', '==', username).limit(1)
    resultados = query.stream()
    for doc in resultados:
        dados_usuario = doc.to_dict()
        seguidores = dados_usuario.get('seguidores', [])
        return seguidores
    return {"erro": "Usuário não encontrado"}, 404
     
def buscar_usuario_por_id(user_id):
    usuario_ref = db.collection('Usuarios').document(user_id)
    usuario = usuario_ref.get()

    if not usuario.exists:
        return jsonify({'erro': 'Usuário não encontrado!'}), 404

    return usuario.to_dict()
