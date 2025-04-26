from flask import Blueprint, request, jsonify
from Services.Usuario_Service import (
    registrar_usuario,
    login_usuario,
    listar_usuarios,
    listar_todos,
    deletar_usuario,
    editar_usuario
)

usuario_bp = Blueprint('usuario_bp', __name__)


@usuario_bp.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()

    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    esporte_id = data.get('esporte_id')
    estado = data.get('estado')

    if not email or not senha or not esporte_id or not nome or not estado:
        return jsonify({"erro": "Campos 'email', 'senha' , 'nome' , 'estado' e 'esporte_id' são obrigatórios"}), 400

    resposta, status = registrar_usuario(nome, email, senha, esporte_id, estado)
    return jsonify(resposta), status



@usuario_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "Campos 'email' e 'senha' são obrigatórios"}), 400

    resposta, status = login_usuario(email, senha)
    return jsonify(resposta), status




@usuario_bp.route('/usuarios', methods=['GET'])
def listar():
    usuarios = listar_usuarios()
    return jsonify(usuarios), 200




@usuario_bp.route('/usuarios/todos', methods=['GET'])
def listar_completo():
    usuarios = listar_todos()
    return jsonify(usuarios), 200




@usuario_bp.route('/usuarios/<usuario_id>', methods=['DELETE'])
def deletar(usuario_id):
    resposta, status = deletar_usuario(usuario_id)
    return jsonify(resposta), status




@usuario_bp.route('/usuarios/<usuario_id>', methods=['PUT'])
def editar(usuario_id):
    novos_dados = request.get_json()

    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400

    resposta, status = editar_usuario(usuario_id, novos_dados)
    return jsonify(resposta), status
