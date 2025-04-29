from flask import Blueprint, request, jsonify
from Services.Comentario_Service import (
    criar_comentario,
    listar_comentarios,
    listar_comentarios_por_postagem,
    listar_comentarios_por_usuario,
    deletar_comentario_por_id,
    editar_comentario_por_id,
    alterar_status_comentario
)

comentario_bp = Blueprint('comentario_bp', __name__, url_prefix="/comentario")



# Rota para Criar Comentário
@comentario_bp.route('/CriarComentario', methods=['POST'])
def criarComentario():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do comentário não fornecidos"}), 400

    usuario_id = data.get('usuario_id')
    postagem_id = data.get('postagem_id')
    conteudo = data.get('conteudo')
    status_comentario = data.get('status_comentario', 'ativo')

    if not usuario_id or not postagem_id or not conteudo:
        return jsonify({"erro": "Campos 'usuario_id', 'postagem_id' e 'conteudo' são obrigatórios"}), 400

    resposta, status = criar_comentario(usuario_id, postagem_id, conteudo, status_comentario)
    return jsonify(resposta), status



# Rota para Listar Comentários
@comentario_bp.route('/ListarComentarios', methods=['GET'])
def listarComentarios():
    try:
        comentarios = listar_comentarios()
        return jsonify(comentarios), 200
    except Exception as e:
        print(f"Erro na rota listarComentarios: {e}")
        return jsonify({"erro": "Erro interno ao listar comentários"}), 500



# Rota para Listar Comentários de uma Postagem
@comentario_bp.route('/ListarComentariosPorPostagem/<postagem_id>', methods=['GET'])
def listarComentariosPorPostagem(postagem_id):
    try:
        comentarios = listar_comentarios_por_postagem(postagem_id)
        return jsonify(comentarios), 200
    except Exception as e:
        print(f"Erro na rota listarComentariosPorPostagem: {e}")
        return jsonify({"erro": "Erro interno ao listar comentários da postagem"}), 500



# Rota para Listar Comentários de um Usuário
@comentario_bp.route('/ListarComentariosPorUsuario/<usuario_id>', methods=['GET'])
def listarComentariosPorUsuario(usuario_id):
    try:
        comentarios = listar_comentarios_por_usuario(usuario_id)
        return jsonify(comentarios), 200
    except Exception as e:
        print(f"Erro na rota listarComentariosPorUsuario: {e}")
        return jsonify({"erro": "Erro interno ao listar comentários do usuário"}), 500



# Rota para Deletar Comentário por ID
@comentario_bp.route('/ExcluirComentario/<comentario_id>', methods=['DELETE'])
def deletarComentario(comentario_id):
    resposta, status = deletar_comentario_por_id(comentario_id)
    return jsonify(resposta), status




# Rota para Editar Comentário por ID
@comentario_bp.route('/EditarComentario/<comentario_id>', methods=['PUT'])
def editarComentario(comentario_id):
    novos_dados = request.get_json()

    if not novos_dados:
        return jsonify({"erro": "Nenhum dado fornecido para atualização"}), 400

    # Remove campos que não devem ser atualizados
    campos_protegidos = ['id', 'usuario_id', 'postagem_id', 'data_criacao']
    for campo in campos_protegidos:
        novos_dados.pop(campo, None)

    resposta, status = editar_comentario_por_id(comentario_id, novos_dados)
    return jsonify(resposta), status




# Rota para Alterar Status do Comentário
@comentario_bp.route('/AlterarStatusComentario/<comentario_id>', methods=['PATCH'])
def alterarStatusComentario(comentario_id):
    data = request.get_json()
    if not data or 'status_comentario' not in data:
        return jsonify({"erro": "Novo status não fornecido"}), 400

    novo_status = data['status_comentario']
    resposta, status = alterar_status_comentario(comentario_id, novo_status)
    return jsonify(resposta), status