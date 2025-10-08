from flask import Blueprint, request, jsonify
from Services import Post_Service


postagem_bp = Blueprint('postagem_bp', __name__, url_prefix="/postagem")


# Rota para Criar Postagem
# Implementado
@postagem_bp.route('/CriarPostagem', methods=['POST'])
def criarPostagem():

    descricao = request.form.get("descricao")
    imagem = request.files.get("imagem")

    post_dict, status = Post_Service.criar_post(
        descricao=descricao,
        imagem=imagem, 
    )

    return post_dict, status



# Rota para Listar Postagens
# Implementado
@postagem_bp.route('/ListarPostagens', methods=['GET'])
def listarPostagens():
    return Post_Service.listar_postagens_minhas()


@postagem_bp.route('/usuario/<string:usuario_id>', methods=['GET'])
def listar_postagens_de_usuario(usuario_id):
    return Post_Service.listar_postagens_de_outro_usuario(usuario_id)


# Implementado
@postagem_bp.route('/ExcluirPostagem', methods=['POST'])
def ExcluirPostagem():
    dados = request.get_json()

    if not dados or 'postagem_id' not in dados:
        return {"erro": "ID da postagem não fornecido."}, 400

    postagem_id = dados['postagem_id']

    return Post_Service.deletar_postagem_por_Postid(postagem_id)

@postagem_bp.route('/AdicionarComentario', methods=['POST'])
def adicionarComentario():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados não fornecidos."}), 400

    post_id = dados.get("post_id")
    texto_comentario = dados.get("comentario")

    if not post_id or not texto_comentario:
        return jsonify({"erro": "Campos 'post_id' e 'comentario' são obrigatórios."}), 400
    return Post_Service.adicionar_comentario(post_id, texto_comentario)


@postagem_bp.route('/ListarComentarios/<string:post_id>', methods=['GET'])
def listar_comentarios(post_id):
    try:
        comentarios = Post_Service.listar_comentarios_por_post(post_id)
        return jsonify(comentarios), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@postagem_bp.route('/DeletarComentario', methods=['POST'])
def deletarComentario():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Dados não fornecidos."}), 400
    
    post_id = dados.get("post_id")
    comentario_id = dados.get("comentario_id")

    if not post_id or not comentario_id:
        return jsonify({"erro": "Campos 'post_id' e 'comentario' são obrigatórios."}), 400
    
    return Post_Service.deletar_comentario_por_id(post_id,comentario_id)

# Implementado
@postagem_bp.route('/EditarPostagem', methods=['PUT'])
def EditarPostagem():
    post_id = request.form.get("post_id")

    if not post_id:
        return jsonify({"erro": "O campo 'post_id' é obrigatório."}), 400
    

    descricao = request.form.get("descricao")
    imagem = request.files.get("imagem")

    post_dict, status = Post_Service.editar_postagem_por_id(
        post_id=post_id,
        descricao=descricao,
        imagem=imagem, 
    )

    return jsonify(post_dict), status


# Implementado
@postagem_bp.route('/FeedSemFiltro', methods=['GET'])
def FeedSemFiltro():
    resultado = Post_Service.feed_sem_filtro()
    return jsonify(resultado)

# Implementado

@postagem_bp.route("/FeedSeguindo", methods=["GET"])
def feed():
    try:
        resultado = Post_Service.feed_seguindos()
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
