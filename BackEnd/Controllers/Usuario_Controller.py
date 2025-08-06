from flask import Blueprint, json, request, jsonify, g
from middlewares.generate_token import generate_token
from middlewares.auth_token import token_required
import Services.Usuario_Service as usuario_service

usuario_bp = Blueprint('usuario_bp', __name__, url_prefix="/usuario" )


# Implementado
@usuario_bp.route('/RegistrarUsuario', methods=['POST'])
def registrarUsuario():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados do formulário não fornecidos"}), 400

    nome_completo = data.get('NomeCompleto')
    username = data.get('username')
    data_nascimento = data.get('data_nascimento')
    email = data.get('email')
    senha = data.get('senha')

    if not all([nome_completo, username, data_nascimento, email, senha]):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    resultado = usuario_service.registrar_usuario(nome_completo, username, data_nascimento, email, senha)

    if isinstance(resultado, tuple):
        return jsonify(resultado[0]), resultado[1]

    return jsonify(resultado), 400


# Implementado
@usuario_bp.route('/LoginUsuario', methods=['POST'])
def loginUsuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "Campos 'email' e 'senha' são obrigatórios"}), 400

    resposta, status = usuario_service.login_usuario(email, senha)
    return jsonify(resposta), status


# Implementado
@usuario_bp.route('/DadosModal', methods=['POST'])
def adicionar_informacoes():
    try:
        dados = json.loads(request.form.get('dados', '{}'))
        arquivo_foto = request.files.get('foto')

        resposta, status = usuario_service.adicionar_dados_modal(dados, arquivo_foto)
        return jsonify(resposta), status

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@usuario_bp.route('/MeuPerfil', methods=['GET'])
def meu_perfil():
    try:
        dados = json.loads(request.form.get('dados', '{}'))
        arquivo_foto = request.files.get('foto')

        resposta, status = usuario_service.adicionar_dados_modal(dados, arquivo_foto)
        return jsonify(resposta), status

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@usuario_bp.route('/EditarUsuario', methods=['PUT'])
def editar():
    novos_dados = request.get_json()

    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400

    resposta, status = usuario_service.editar_usuario_por_id(novos_dados)

    return jsonify(resposta), status


# Implementado
@usuario_bp.route('/follow', methods=['POST'])
def seguir_usuario():
    dados = request.get_json()
    seguido_id = dados.get('seguido_id')

    if not seguido_id:
        return jsonify({'erro': 'ID do usuário a ser seguido é obrigatório'}), 400

    resposta, status = usuario_service.seguir_usuario(seguido_id)
    return jsonify(resposta), status

# Implementado
@usuario_bp.route('/unfollow', methods=['POST'])
def deixar_de_seguir_usuario():
    dados = request.get_json()
    seguido_id = dados.get('seguido_id')

    if not seguido_id:
        return jsonify({'erro': 'ID do usuário a ser removido é obrigatório'}), 400

    resposta, status = usuario_service.deixar_de_seguir_usuario(seguido_id)
    return jsonify(resposta), status


# Implementado
@usuario_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    resposta, status = usuario_service.listar_usuarios()
    return jsonify(resposta), status