from firebase_admin import firestore, storage
from flask import g, jsonify
from middlewares.auth_token import token_required
from Models.Post_Model import Postagem
from google.cloud.firestore import ArrayUnion


db = firestore.client()
bucket = storage.bucket()


# Função para Criar Postagem
# Implementado
@token_required
def criar_post(descricao, imagem=None, status_postagem='ativo', comentarios=None, contador_curtidas=0):
    usuario_id = g.user_id
    user_ref = db.collection('Usuarios').document(usuario_id)

    postagem = Postagem(
        usuario_id=usuario_id,
        descricao=descricao,
        imagem='',
        status_postagem=status_postagem,
        comentarios=comentarios,
        contador_curtidas=contador_curtidas
    )

    if imagem:
        caminho = f"Usuarios/{usuario_id}/Fotos/post_{postagem.id}.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(imagem, content_type=imagem.content_type)
        blob.make_public()
        postagem.imagem = blob.public_url

    db.collection('Postagens').document(postagem.id).set(postagem.to_dict())

    user_ref.update({
        'post_criados': ArrayUnion([postagem.id])
    })

    return postagem.to_dict(), 201



# Função para Listar Postagens
# Implementado
@token_required
def listar_postagens_UserID():
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
    # Buscar as 10 últimas postagens (ordem decrescente por data_criacao)
    postagens_ref = db.collection("Postagens").order_by("data_criacao", direction=firestore.Query.DESCENDING).limit(10)
    postagens_docs = postagens_ref.stream()

    resultado = []

    for doc in postagens_docs:
        postagem_data = doc.to_dict()
        postagem_data["id"] = doc.id

        usuario_id = postagem_data.get("usuario_id")
        if usuario_id:
            usuario_ref = db.collection("Usuarios").document(usuario_id)
            usuario_doc = usuario_ref.get()
            if usuario_doc.exists:
                usuario_data = usuario_doc.to_dict()
                usuario_data["id"] = usuario_doc.id

                resultado.append({
                    "postagem": postagem_data,
                    "usuario": usuario_data
                })

    return resultado