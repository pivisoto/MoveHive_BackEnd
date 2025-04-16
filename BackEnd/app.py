from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt 

app = Flask(__name__)

cred = credentials.Certificate("move-hive-firebase-adminsdk-fbsvc-0334323fd4.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    return 'Conexão com Firebase funcionando!'

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    if not email:
        return jsonify({"erro": "Campo 'email' é obrigatório"}), 400
    if not senha:
        return jsonify({"erro": "Campo 'senha' é obrigatório"}), 400
    
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('email', '==', email).limit(1)
    docs = query.stream()

    if any(docs):
        return jsonify({"erro": "E-mail já cadastrado"}), 400
    salt = bcrypt.gensalt()
    senha = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
    usuario_data = {
            'email': email,
            'senha': senha
        }
    doc_ref = db.collection('Usuarios').add(usuario_data)
    return jsonify({"status": "sucesso", "id": doc_ref[1].id})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    if not email:
        return jsonify({"erro": "Campo 'email' é obrigatório"}), 400
    if not senha:
        return jsonify({"erro": "Campo 'senha' é obrigatório"}), 400
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('email', '==', email).limit(1)
    docs = query.stream()

    usuario = next(docs, None)
    if not usuario:
        return jsonify({"erro": "E-mail não encontrado"}), 400

    senha_hash = usuario.to_dict().get('senha')
    if not senha_hash:
        return jsonify({"erro": "Senha não encontrada"}), 400

    if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
        return jsonify({"status": "sucesso", "mensagem": "Login bem-sucedido"}), 200
    else:
        return jsonify({"erro": "Senha incorreta"}), 400

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios_ref = db.collection('Usuarios').stream()
    usuarios = [{doc.id: doc.to_dict()} for doc in usuarios_ref]
    return jsonify(usuarios)

if __name__ == '__main__':
    app.run(debug=True)