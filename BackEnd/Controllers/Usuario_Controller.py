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
@usuario_bp.route('/usuariosSemFiltro', methods=['GET'])
def listar_usuarios_sem_filtro():
    resposta, status = usuario_service.listar_usuarios_sem_filtro()
    return jsonify(resposta), status

# Implementado
@usuario_bp.route('/usuariosComFiltro', methods=['GET'])
def listar_usuarios_com_filtro():
    resposta, status = usuario_service.listar_usuarios_com_filtro()
    return jsonify(resposta), status

# Implementado
@usuario_bp.route('/usuariosSeguidos', methods=['GET'])
def listar_usuarios_seguidos():
    resposta, status = usuario_service.listar_usuarios_seguindo()
    return jsonify(resposta), status

# Implementado
@usuario_bp.route('/rankingTodos', methods=['GET'])
def ranking_usuario_todos():
    return usuario_service.competicao_usuarios_todos()

# Implementado
@usuario_bp.route('/rankingSeguindo', methods=['GET'])
def ranking_usuarios_seguindo():
    return usuario_service.competicao_usuarios_seguindo()

# Implementado
@usuario_bp.route('/esqueciSenha', methods=['POST'])
def esqueci_senha():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"erro": "Corpo da requisição não pode ser vazio."}), 400
    except Exception:
        return jsonify({"erro": "Formato de requisição inválido. Esperado um JSON."}), 400

    email = data.get('email')

    if not email:
        return jsonify({"erro": "Formato de e-mail inválido ou ausente."}), 400

    resultado = usuario_service.solicitar_reset_senha(email)

    return jsonify(resultado), 200

# Implementado
@usuario_bp.route('/resetarSenha', methods=['POST'])
def resetar():
    data = request.json
    token = data.get('token')
    nova_senha = data.get('nova_senha')

    if not token or not nova_senha:
        return jsonify({"erro": "Token e nova senha são obrigatórios."}), 400

    status, mensagem = usuario_service.resetar_senha(token, nova_senha)

    if status == 'SUCESSO':
        return jsonify({"msg": mensagem}), 200
        
    elif status == 'TOKEN_INVALIDO':
        return jsonify({"erro": mensagem}), 404  # Not Found
        
    elif status == 'TOKEN_EXPIRADO':
        return jsonify({"erro": mensagem}), 400  # Bad Request
           
    else:
        return jsonify({"erro": "Ocorreu um erro interno no servidor."}), 500