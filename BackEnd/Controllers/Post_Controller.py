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