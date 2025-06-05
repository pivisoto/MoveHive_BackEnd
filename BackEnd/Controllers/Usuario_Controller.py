from flask import Blueprint, json, request, jsonify, g
from middlewares.generate_token import generate_token
from middlewares.auth_token import token_required
import Services.Usuario_Service as usuario_service

usuario_bp = Blueprint('usuario_bp', __name__, url_prefix="/usuario" )


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


@usuario_bp.route('/LoginUsuario', methods=['POST'])
def loginUsuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "Campos 'email' e 'senha' são obrigatórios"}), 400

    resposta, status = usuario_service.login_usuario(email, senha)
    return jsonify(resposta), status



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



@usuario_bp.route('/ListarUsuarios', methods=['GET'])
def listarUsuarios():
    try:
        usuarios = usuario_service.listar_usuarios()
        return jsonify(usuarios), 200
    except Exception as e:
        print(f"Erro na rota listarUsuarios: {e}")
        return jsonify({"erro": "Erro interno ao listarUsuarios"}), 500


#exemplo http://localhost:5000/ListarSeguindo?username=joao
@usuario_bp.route('/ListarSeguindo', methods=['GET'])
def listarSeguidores():
    try:
        solicitacao = request.args.get('username')
        seguindo = usuario_service.listar_seguindo(solicitacao)
        return jsonify(seguindo), 200
    except Exception as e:
        print(f"Erro na rota listarUsuarios: {e}")
        return jsonify({"erro": "Erro interno ao listarSeguindo"}), 500


@usuario_bp.route('/ListarSeguidores', methods=['GET'])
def listarSeguindo():
    try:
        solicitacao = request.args.get('username')
        seguindo = usuario_service.listar_seguidores(solicitacao)
        return jsonify(seguindo), 200
    except Exception as e:
        print(f"Erro na rota listarUsuarios: {e}")
        return jsonify({"erro": "Erro interno ao listarSeguidores"}), 500


@usuario_bp.route('/ExcluirUsuario/<usuario_id>', methods=['DELETE'])  
def deletar_por_ID(usuario_id):
    resposta, status = usuario_service.deletar_usuario_por_id(usuario_id)
    return jsonify(resposta), status




@usuario_bp.route('/EditarUsuario', methods=['PUT'])
def editar():
    novos_dados = request.get_json()

    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400

    resposta, status = usuario_service.editar_usuario_por_id(novos_dados)

    return jsonify(resposta), status


#exemplo http://127.0.0.1:5000/usuario/ToggleSeguir
# utiliza, username de quem a pessoa quer seguir {"username":"pivisoto"}
@usuario_bp.route('/ToggleSeguir', methods=['PUT'])
def toggle_seguir():
    solicitacao = request.get_json()
    if not solicitacao:
        return jsonify({"erro": "Nenhum usuario para seguir"}), 400
    resposta, status = usuario_service.toggle_seguir_usuario(solicitacao)

    return jsonify(resposta), status


@usuario_bp.route('/BuscarUsuarioID', methods=['GET'])
def buscar_usuario_por_id():
    user_id = g.user_id
    dados_usuario = usuario_service.buscar_usuario_por_id(user_id)

    if not dados_usuario:
        return jsonify({'erro': 'Usuário não encontrado!'}), 404

    return jsonify({
        'status': 'sucesso',
        'usuario': dados_usuario
    }), 200 