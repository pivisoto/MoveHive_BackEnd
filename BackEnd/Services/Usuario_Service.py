import bcrypt
from firebase_admin import firestore, credentials
from Models.Usuario_Model import Usuario
import firebase_admin

if not firebase_admin._apps:
    cred = credentials.Certificate("move-hive-firebase-adminsdk-fbsvc-0334323fd4.json")
    firebase_admin.initialize_app(cred)



db = firestore.client()



def registrar_usuario(nome, email, senha, esporte_id, estado):
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('email', '==', email).limit(1)
    docs = query.stream()

    if any(docs):
        return {"erro": "E-mail já cadastrado"}, 400

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    usuario = Usuario(nome=nome, email=email, senha=senha_hash, esporte_id=esporte_id, estado=estado)

    doc_ref = usuarios_ref.document(usuario.id)
    doc_ref.set(usuario.to_dict())

    return {"status": "sucesso", "id": doc_ref.id}, 201




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

    return {"status": "sucesso", "mensagem": "Login bem-sucedido"}, 200



def listar_usuarios():
    usuarios_ref = db.collection('Usuarios').stream()
    return [{doc.id: doc.to_dict()} for doc in usuarios_ref]



def listar_todos():
    usuarios = db.collection('Usuarios').stream()
    lista = []
    for doc in usuarios:
        dados = doc.to_dict()
        dados['id'] = doc.id  # garante que o ID esteja no objeto
        lista.append(dados)   # adiciona como item direto da lista
    return lista



def deletar_usuario(usuario_id):
    """Deleta um usuário pelo ID."""
    doc_ref = db.collection('Usuarios').document(usuario_id)
    if not doc_ref.get().exists:
        return {"erro": "Usuário não encontrado"}, 404

    doc_ref.delete()
    return {"status": "sucesso", "mensagem": "Usuário deletado com sucesso"}, 200



def editar_usuario(usuario_id, novos_dados):
    """Edita dados do usuário. A senha será re-hashada se fornecida."""
    doc_ref = db.collection('Usuarios').document(usuario_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return {"erro": "Usuário não encontrado"}, 404

    dados_atualizados = novos_dados.copy()

    if 'senha' in novos_dados:
        dados_atualizados['senha'] = bcrypt.hashpw(novos_dados['senha'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    doc_ref.update(dados_atualizados)
    return {"status": "sucesso", "mensagem": "Usuário atualizado com sucesso"}, 200
