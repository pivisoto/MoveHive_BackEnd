from firebase_admin import firestore, storage
from flask import g, jsonify
from middlewares.auth_token import token_required
from Models.Post_Model import Postagem
from google.cloud.firestore import ArrayUnion
import uuid
from .Notificacao_Service import criar_notificacao, deletar_notificacao


db = firestore.client()
bucket = storage.bucket()


# Função para Criar Postagem
# Implementado
@token_required
def criar_post(descricao, imagem=None, status_postagem='ativo', comentarios=None, contador_curtidas=0):
    usuario_id = g.user_id
    # Tenta buscar usuário normal
    user_ref = db.collection('Usuarios').document(usuario_id)
    user_doc = user_ref.get()
    pasta_bucket = f"Usuarios/{usuario_id}/Fotos/"

    # Se não existir, tenta empresa
    if not user_doc.exists:
        user_ref = db.collection('UsuariosEmpresa').document(usuario_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            return {"erro": "Usuário ou empresa não encontrado"}, 404
        pasta_bucket = f"UsuariosEmpresa/{usuario_id}/Fotos/"

    postagem = Postagem(
        usuario_id=usuario_id,
        descricao=descricao,
        imagem='',
        status_postagem=status_postagem,
        comentarios=comentarios,
        contador_curtidas=contador_curtidas
    )

    # Upload da imagem, se existir
    if imagem:
        caminho = f"{pasta_bucket}post_{postagem.id}.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(imagem, content_type=imagem.content_type)
        blob.make_public()
        postagem.imagem = blob.public_url

    # Salva postagem
    db.collection('Postagens').document(postagem.id).set(postagem.to_dict())

    # Atualiza lista de post_criados na coleção correta
    user_ref.update({
        'post_criados': firestore.ArrayUnion([postagem.id])
    })

    return postagem.to_dict(), 201

@token_required
def toggle_curtida(post_id):
    usuario_id = g.user_id
    try:
        post_ref = db.collection("Postagens").document(post_id)
        post_doc = post_ref.get()
        curtidas = post_doc.to_dict().get("curtidas", [])
        dono_post = post_doc.to_dict().get("usuario_id")
        if not post_doc.exists:
            return {"erro": "Postagem não encontrada."}, 404
        
        requisicao_curtida = {"usuario_id": usuario_id,}

        usuario_ref = db.collection("Usuarios").document(usuario_id)
        usuario_doc = usuario_ref.get()
        
        if usuario_doc.exists:
            username = usuario_doc.to_dict().get("username")
            print(f"O nome de usuário é: {username}")
        else:
            print("Usuário não encontrado.")
        
        usuario_ja_curtiu = any(curtida.get("usuario_id") == usuario_id for curtida in curtidas)

        if usuario_ja_curtiu:
            post_ref.update({
                "curtidas": firestore.ArrayRemove([requisicao_curtida]),
                "contador_curtidas": firestore.Increment(-1)
            })
            notificacao_query = db.collection("Notificacoes").where("tipo", "==", "Curtida").where("referencia_id", "==", post_id).where("usuario_origem_id", "==", usuario_id).limit(1)
            docs = notificacao_query.get()
            notificacao_doc = docs[0]
            deletar_notificacao(notificacao_doc.id)
            return {"mensagem": "Removendo curtida."}, 200
        else:
            post_ref.update({
                "curtidas": firestore.ArrayUnion([requisicao_curtida]),
                "contador_curtidas": firestore.Increment(1)
            })
            mensagem = f"{username} curtiu seu post"
            criar_notificacao(dono_post,"Curtida",post_id,mensagem)
            return {"mensagem": "Post curtido com sucesso!"}, 201

    except Exception as e:
        return {"erro": f"Erro ao modificar curtida: {str(e)}"}, 500
    
@token_required
def adicionar_comentario(post_id, texto_comentario):
    usuario_id = g.user_id
    if not texto_comentario:
        return {"erro": "O campo 'comentario' é obrigatório."}, 400

    try:
        post_ref = db.collection("Postagens").document(post_id)
        post_doc = post_ref.get()
        dono_post = post_doc.to_dict().get("usuario_id")
        if not post_doc.exists:
            return {"erro": "Postagem não encontrada."}, 404
        
        comentario_id = str(uuid.uuid4())
        novo_comentario = {
            "comentario_id": comentario_id,
            "usuario_id": usuario_id,
            "comentario": texto_comentario
        }

        post_ref.update({
            "comentarios": firestore.ArrayUnion([novo_comentario])
        })

        usuario_ref = db.collection("Usuarios").document(usuario_id)
        usuario_doc = usuario_ref.get()

        if usuario_doc.exists:
            username = usuario_doc.to_dict().get("username")
            print(f"O nome de usuário é: {username}")
        else:
            print("Usuário não encontrado.")
        mensagem = f"{username} comentou em seu post: {texto_comentario}"
        criar_notificacao(dono_post,"Comentario",post_id,mensagem)
        return {
            "mensagem": "Comentário adicionado com sucesso!",
            "comentario": novo_comentario
        }, 201

    except Exception as e:
        return {"erro": f"Erro ao adicionar comentário: {str(e)}"}, 500
    
def listar_comentarios_por_post(post_id):
    try:
        post_ref = db.collection("Postagens").document(post_id).get()
        if not post_ref.exists:
            return {"erro": "Postagem não encontrada."}, 404

        post_data = post_ref.to_dict()
        comentarios = post_data.get("comentarios", [])
        return comentarios, 200
    except Exception as e:
        return {"erro": f"Erro ao listar comentários: {str(e)}"}, 500

@token_required
def deletar_comentario_por_id(post_id,comentario_id):
    usuario_id = g.user_id
    try:
        post_ref = db.collection("Postagens").document(post_id)
        post_doc = post_ref.get()

        if not post_doc.exists:
            return {"erro": "Postagem não encontrada."}, 404

        post_data = post_doc.to_dict()
        comentarios = post_data.get("comentarios", [])

        comentario_encontrado = None
        for comentario in comentarios:
            if comentario.get("comentario_id") == comentario_id:
                comentario_encontrado = comentario
                break

        if not comentario_encontrado:
            return {"erro": "Comentário não encontrado."}, 404

        if comentario_encontrado.get("usuario_id") != usuario_id:
            return {"erro": "Você não tem permissão para excluir este comentário."}, 403

        novos_comentarios = [comentario for comentario in comentarios if comentario.get("comentario_id") != comentario_id]

        post_ref.update({"comentarios": novos_comentarios})

        return {"mensagem": "Comentário removido com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao deletar comentário: {str(e)}"}, 500


# Função para Listar Postagens
# Implementado
@token_required
def listar_postagens_minhas():
    usuario_id = g.user_id

    try:
        postagens_ref = db.collection('Postagens').where('usuario_id', '==', usuario_id)
        docs = postagens_ref.stream()

        lista_postagens = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  # Inclui o ID do documento
            lista_postagens.append(data)

        return jsonify(lista_postagens), 200

    except Exception as e:
        return jsonify({'mensagem': 'Erro ao buscar postagens.', 'erro': str(e)}), 500



@token_required
def listar_postagens_de_outro_usuario(usuario_id):

    try:
        postagens_ref = db.collection('Postagens').where('usuario_id', '==', usuario_id)
        docs = postagens_ref.stream()

        lista_postagens = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  
            lista_postagens.append(data)
        
        lista_postagens.sort(key=lambda x: x.get('data_criacao'), reverse=True)

        return jsonify(lista_postagens), 200

    except Exception as e:
        print(f"Erro ao buscar postagens do usuário {usuario_id}: {e}")
        return jsonify({'mensagem': 'Erro ao buscar postagens.', 'erro': str(e)}), 500



# Função para Deletar Postagem por ID
# Implementado
@token_required
def deletar_postagem_por_Postid(postagem_id):
    usuario_id = g.user_id

    user_ref = db.collection('Usuarios').document(usuario_id)
    postagem_ref = db.collection('Postagens').document(postagem_id)

    postagem_doc = postagem_ref.get()

    if not postagem_doc.exists:
        return {"erro": "Postagem não encontrada."}, 404

    postagem_data = postagem_doc.to_dict()

    if postagem_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para excluir esta postagem."}, 403

    try:
        caminho = f"Usuarios/{usuario_id}/Fotos/post_{postagem_id}.jpg"
        blob = bucket.blob(caminho)
        if blob.exists():
            blob.delete()
            print(f"Imagem {caminho} excluída do Storage.")
        else:
            print(f"Nenhuma imagem encontrada em {caminho} para excluir.")
    except Exception as e:
        print(f"Erro ao excluir a imagem: {e}")

    postagem_ref.delete()

    user_ref.update({
        'post_criados': firestore.ArrayRemove([postagem_id])
    })

    return {"mensagem": "Postagem excluída com sucesso."}, 200



# Função para Editar Postagem por ID
# Implementado
@token_required
def editar_postagem_por_id(post_id, descricao=None, imagem=None):
    usuario_id = g.user_id

    user_ref = db.collection('Usuarios').document(usuario_id)
    post_ref = db.collection('Postagens').document(post_id)

    post_doc = post_ref.get()

    if not post_doc.exists:
        return {"erro": "Treino não encontrado."}, 404
    
    post_data = post_doc.to_dict()

    if post_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para atualizar este treino."}, 403

    updates = {}

    if descricao is not None:
        updates['descricao'] = descricao

    if imagem:
        try:
            caminho = f"Usuarios/{usuario_id}/Fotos/post_{post_id}.jpg"
            blob = bucket.blob(caminho)

            import time
            imagem.seek(0) 

            blob.upload_from_file(imagem, content_type=imagem.content_type)
            blob.make_public()

            timestamp = int(time.time())
            url_para_salvar_no_firestore = f"{blob.public_url}?v={timestamp}"

            updates['imagem'] = url_para_salvar_no_firestore

        except Exception as e:
         return {"erro": f"Erro ao fazer upload da imagem: {str(e)}"}, 500

    post_ref.update(updates)

    return {"mensagem": "Postagem atualizada com sucesso."}, 200



# Implementado
@token_required
def feed_sem_filtro():
    usuario_id = g.user_id  # usuário logado

    usuario_ref = db.collection("Usuarios").document(usuario_id)
    usuario_doc = usuario_ref.get()

    # Se não existe, tenta empresa
    if not usuario_doc.exists:
        usuario_ref = db.collection("UsuariosEmpresa").document(usuario_id)
        usuario_doc = usuario_ref.get()
        if not usuario_doc.exists:
            return {"erro": "Usuário não encontrado"}, 404

    usuario_data = usuario_doc.to_dict()
    seguindo = usuario_data.get("seguindo", [])
    if not isinstance(seguindo, list):
        seguindo = list(seguindo) if seguindo else []

    # Buscar todas postagens em ordem decrescente
    postagens_ref = db.collection("Postagens").order_by("data_criacao", direction=firestore.Query.DESCENDING)
    postagens_docs = postagens_ref.stream()

    resultado = []

    for doc in postagens_docs:
        postagem_data = doc.to_dict()
        postagem_data["id"] = doc.id

        usuario_id_post = postagem_data.get("usuario_id")

        # Ignorar posts de quem o usuário/empresa segue ou do próprio
        if usuario_id_post and usuario_id_post not in seguindo and usuario_id_post != usuario_id:
            # Primeiro tenta buscar na coleção Usuarios
            usuario_ref_post = db.collection("Usuarios").document(usuario_id_post)
            usuario_doc_post = usuario_ref_post.get()

            # Se não existir, tenta UsuariosEmpresa
            if not usuario_doc_post.exists:
                usuario_ref_post = db.collection("UsuariosEmpresa").document(usuario_id_post)
                usuario_doc_post = usuario_ref_post.get()

            if usuario_doc_post.exists:
                usuario_data_post = usuario_doc_post.to_dict()
                usuario_data_post["id"] = usuario_doc_post.id

                resultado.append({
                    "postagem": postagem_data,
                    "usuario": usuario_data_post
                })

    return resultado


# Implementado
@token_required
def feed_seguindos():
    usuario_id = g.user_id  # usuário logado

    # Tenta buscar usuário normal
    usuario_ref = db.collection("Usuarios").document(usuario_id)
    usuario_doc = usuario_ref.get()

    # Se não existe, tenta empresa
    if not usuario_doc.exists:
        usuario_ref = db.collection("UsuariosEmpresa").document(usuario_id)
        usuario_doc = usuario_ref.get()
        if not usuario_doc.exists:
            return {"erro": "Usuário não encontrado"}, 404

    usuario_data = usuario_doc.to_dict()
    seguindo = usuario_data.get("seguindo", [])

    if not seguindo:
        return []

    # Buscar postagens de todos que o usuário/empresa segue
    postagens_ref = (
        db.collection("Postagens")
        .where("usuario_id", "in", seguindo)
        .order_by("data_criacao", direction=firestore.Query.DESCENDING)
        .limit(20)
    )
    postagens_docs = postagens_ref.stream()

    resultado = []
    for doc in postagens_docs:
        postagem_data = doc.to_dict()
        postagem_data["id"] = doc.id

        usuario_id_post = postagem_data.get("usuario_id")
        if usuario_id_post:
            # Primeiro busca na coleção Usuarios
            usuario_ref_post = db.collection("Usuarios").document(usuario_id_post)
            usuario_doc_post = usuario_ref_post.get()

            # Se não existir, tenta UsuariosEmpresa
            if not usuario_doc_post.exists:
                usuario_ref_post = db.collection("UsuariosEmpresa").document(usuario_id_post)
                usuario_doc_post = usuario_ref_post.get()

            if usuario_doc_post.exists:
                usuario_data_post = usuario_doc_post.to_dict()
                usuario_data_post["id"] = usuario_doc_post.id

                resultado.append({
                    "postagem": postagem_data,
                    "usuario": usuario_data_post
                })

    return resultado
