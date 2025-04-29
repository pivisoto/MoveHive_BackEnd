from flask import Blueprint, request, jsonify
from middlewares.token_required import generate_token
from Services.Usuario_Service import (
    registrar_usuario,
    login_usuario,
    listar_usuarios,
    deletar_usuario_por_id,
    editar_usuario_por_id,
    meu_perfil
)

usuario_bp = Blueprint('usuario_bp', __name__, url_prefix="/usuario" )


@usuario_bp.route('/RegistrarUsuario', methods=['POST'])
def registrarUsuario():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do evento não fornecidos"}), 400


    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    esporte_id = data.get('esporte_id')
    estado = data.get('estado')

    if not email or not senha or not esporte_id or not nome or not estado:
        return jsonify({"erro": "Campos 'email', 'senha' , 'nome' , 'estado' e 'esporte_id' são obrigatórios"}), 400

    resposta, status = registrar_usuario(nome, email, senha, esporte_id, estado)
    return jsonify(resposta), status



@usuario_bp.route('/LoginUsuario', methods=['POST'])
def loginUsuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "Campos 'email' e 'senha' são obrigatórios"}), 400

    resposta, status = login_usuario(email, senha)

    return jsonify(resposta), status




@usuario_bp.route('/ListarUsuarios', methods=['GET'])
def listarUsuarios():
    try:
        usuarios = listar_usuarios()
        return jsonify(usuarios), 200
    
    except Exception as e:
        print(f"Erro na rota listarUsuarios: {e}")
        return jsonify({"erro": "Erro interno ao listarUsuarios"}), 500




@usuario_bp.route('/ExcluirUsuario/<usuario_id>', methods=['DELETE'])
def deletarPorID(usuario_id):
    resposta, status = deletar_usuario_por_id(usuario_id)
    return jsonify(resposta), status




@usuario_bp.route('/EditarUsuario/<usuario_id>', methods=['PUT'])
def editar(usuario_id):
    novos_dados = request.get_json()

    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400

    resposta, status = editar_usuario_por_id(usuario_id, novos_dados)
    return jsonify(resposta), status



@usuario_bp.route('/MeuPerfil', methods=['GET'])
def meu_perfil_route():
    return meu_perfil(request)  