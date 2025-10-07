from flask import Blueprint, json, request, jsonify, g
from middlewares.generate_token import generate_token
from middlewares.auth_token import token_required
import Services.UsuarioEmpresa_Service as usuarioEmpresa_service

usuarioEmpresa_bp = Blueprint('usuarioEmpresa_bp', __name__, url_prefix="/usuarioEmpresa" )

# Implementado
@usuarioEmpresa_bp.route('/RegistrarUsuarioEmpresa', methods=['POST'])
def registrarUsuarioEmpresa():
    data = request.get_json()
    if not data:
        return jsonify({"erro": "Dados do formulário não fornecidos"}), 400

    nome = data.get('nome')
    username = data.get('username')
    email = data.get('email')
    senha = data.get('senha')
    cnpj = data.get('cnpj')

    if not all([nome, username, email, senha, cnpj]):
        return jsonify({"erro": "Campos obrigatórios ausentes"}), 400

    resultado = usuarioEmpresa_service.registrar_empresa(
        nome=nome,
        username=username,
        email=email,
        senha=senha,
        cnpj=cnpj,
    )

    if isinstance(resultado, tuple):
        return jsonify(resultado[0]), resultado[1]

    return jsonify(resultado), 400


# Implementado
@usuarioEmpresa_bp.route('/DadosModalEmpresa', methods=['POST'])
def adicionar_informacoes_empresa():
    try:
        dados = json.loads(request.form.get('dados', '{}'))

        arquivo_foto = request.files.get('foto')

        resposta, status = usuarioEmpresa_service.adicionar_dados_modal_empresa(dados, arquivo_foto)

        return jsonify(resposta), status

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# Implementado
@usuarioEmpresa_bp.route('/ListarEmpresas', methods=['GET'])
def listar_usuarios_sem_filtro():
    resposta, status = usuarioEmpresa_service.listar_empresas_sem_filtro()
    return jsonify(resposta), status


