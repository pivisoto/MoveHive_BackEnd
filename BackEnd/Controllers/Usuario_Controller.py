from flask import Blueprint, request, jsonify, g
from middlewares.token_required import generate_token
from middlewares.auth_token import token_required
import Services.Usuario_Service as usuario_service


usuario_bp = Blueprint('usuario_bp', __name__, url_prefix="/usuario" )


@usuario_bp.route('/RegistrarUsuario', methods=['POST'])
def registrarUsuario():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do evento não fornecidos"}), 400

    nome_completo = data.get('nome_completo')
    username = data.get('username')
    email = data.get('email')
    senha = data.get('senha')
    estado = data.get('estado')
    cidade = data.get('cidade')
    esportes_praticados = data.get('esportes_praticados')  

    if not email or not senha or not nome_completo or not estado or not esportes_praticados:
        return jsonify({"erro": "Campos 'email', 'senha', 'nome', 'estado' e 'esportes_praticados' são obrigatórios"}), 400

    resposta, status = usuario_service.registrar_usuario(
        nome_completo, username, email, senha, estado, cidade, esportes_praticados)
    
    
    return jsonify(resposta), status




@usuario_bp.route('/LoginUsuario', methods=['POST'])
def loginUsuario():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"erro": "Campos 'email' e 'senha' são obrigatórios"}), 400

    resposta, status = usuario_service.login_usuario(email, senha)

    return jsonify(resposta), status




@usuario_bp.route('/ListarUsuarios', methods=['GET'])
def listarUsuarios():
    try:
        usuarios = usuario_service.listar_usuarios()
        return jsonify(usuarios), 200
    
    except Exception as e:
        print(f"Erro na rota listarUsuarios: {e}")
        return jsonify({"erro": "Erro interno ao listarUsuarios"}), 500




@usuario_bp.route('/ExcluirUsuario/<usuario_id>', methods=['DELETE'])
@token_required  
def deletar_por_ID(usuario_id):
    resposta, status = usuario_service.deletar_usuario_por_id(usuario_id)
    return jsonify(resposta), status




@usuario_bp.route('/EditarUsuario', methods=['PUT'])
@token_required
def editar():
    novos_dados = request.get_json()

    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400

    resposta, status = usuario_service.editar_usuario_por_id(novos_dados)

    return jsonify(resposta), status




@usuario_bp.route('/BuscarUsuarioID', methods=['GET'])
@token_required  
def buscar_usuario_por_id():
    user_id = g.user_id
    dados_usuario = usuario_service.buscar_usuario_por_id(user_id)

    if not dados_usuario:
        return jsonify({'erro': 'Usuário não encontrado!'}), 404

    return jsonify({
        'status': 'sucesso',
        'usuario': dados_usuario
    }), 200 