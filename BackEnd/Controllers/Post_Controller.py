from flask import Blueprint, request, jsonify
from Services.Post_Service import (
    criar_postagem,
    listar_postagens,
    listar_postagens_por_usuario,
    deletar_postagem_por_id,
    editar_postagem_por_id,
    curtir_postagem
)

postagem_bp = Blueprint('postagem_bp', __name__, url_prefix="/postagem")


# Rota para Criar Postagem
@postagem_bp.route('/CriarPostagem', methods=['POST'])
def criarPostagem():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do evento não fornecidos"}), 400

    usuario_id = data.get('usuario_id')
    conteudo = data.get('conteudo')
    esporte_praticado = data.get('esporte_praticado')
    imagem = data.get('imagem', '')
    status_postagem = data.get('status_postagem', 'ativo')
    contador_curtidas = data.get('contador_curtidas', 0)

    if not usuario_id or not conteudo or not esporte_praticado:
        return jsonify({"erro": "Campos 'usuario_id', 'conteudo' e 'esporte_praticado' são obrigatórios"}), 400

    resposta, status = criar_postagem(usuario_id, conteudo, esporte_praticado, imagem, status_postagem, contador_curtidas)
    return jsonify(resposta), status


# Rota para Listar Postagens
@postagem_bp.route('/ListarPostagens', methods=['GET'])
def listarPostagens():
    try:
        postagens = listar_postagens()
        return jsonify(postagens), 200
    except Exception as e:
        print(f"Erro na rota listarPostagens: {e}")
        return jsonify({"erro": "Erro interno ao listar postagens"}), 500


# Rota para Listar Postagens de um Usuário
@postagem_bp.route('/ListarPostagensPorUsuario/<usuario_id>', methods=['GET'])
def listarPostagensPorUsuario(usuario_id):
    try:
        postagens = listar_postagens_por_usuario(usuario_id)
        return jsonify(postagens), 200
    except Exception as e:
        print(f"Erro na rota listarPostagensPorUsuario: {e}")
        return jsonify({"erro": "Erro interno ao listar postagens do usuário"}), 500


# Rota para Deletar Postagem por ID
@postagem_bp.route('/ExcluirPostagem/<postagem_id>', methods=['DELETE'])
def deletarPostagem(postagem_id):
    resposta, status = deletar_postagem_por_id(postagem_id)
    return jsonify(resposta), status


# Rota para Editar Postagem por ID
@postagem_bp.route('/EditarPostagem/<postagem_id>', methods=['PUT'])
def editarPostagem(postagem_id):
    novos_dados = request.get_json()

    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400

    resposta, status = editar_postagem_por_id(postagem_id, novos_dados)
    return jsonify(resposta), status


# Rota para Curtir Postagem
@postagem_bp.route('/CurtirPostagem/<postagem_id>', methods=['POST'])
def curtirPostagem(postagem_id):
    resposta, status = curtir_postagem(postagem_id)
    return jsonify(resposta), status
