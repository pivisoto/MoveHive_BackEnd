from firebase_admin import firestore, storage
from flask import g, jsonify
from middlewares.auth_token import token_required
from Models.Chat_Model import Chat
from google.cloud.firestore import ArrayUnion
from .Notificacao_Service import criar_notificacao, deletar_notificacao
import uuid
from time import sleep

db = firestore.client()
bucket = storage.bucket()


#testado
@token_required
def criar_chat(nome_chat,lista_participantes,id_evento,foto_chat=None):
    usuario_id = g.user_id
    if not lista_participantes:
        lista_participantes = []
    timestamp_atual = firestore.SERVER_TIMESTAMP 
    ultima_visualizacao_por_usuario = {}
    for usuario in lista_participantes:
        ultima_visualizacao_por_usuario[f'{usuario}'] = timestamp_atual
    
    chat = Chat(
        user_adm=usuario_id,
        nome_chat=nome_chat,
        participantes=lista_participantes,
        ultima_mensagem="Chat novo!",
        horario_ultima_mensagem=timestamp_atual,
        ultima_visualizacao_por_usuario=ultima_visualizacao_por_usuario,
        id_evento=id_evento,
        foto_chat=foto_chat
    )
    
    if id_evento == '':
        caminho = f"Usuarios/{usuario_id}/Fotos/chat_{chat.id}.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(caminho, content_type=chat.content_type)
        blob.make_public()
        chat.foto_chat = blob.public_url
    
    chat_dict = chat.to_dict()

    db.collection('Chat').document(chat.id).set(chat_dict)

    return jsonify("Chat criado com sucesso"), 201

#testado
@token_required
def adicionar_ao_chat(id_recebido, novos_participantes):
    usuario_id = g.user_id
    chats_ref = db.collection("Chat")
    chat_ref = chats_ref.document(id_recebido)
    chat_doc = chat_ref.get()
    encontrado_por_evento = False  

    if not chat_doc.exists:
        query = chats_ref.where("id_evento", "==", id_recebido).limit(1).get()
        if query:
            chat_ref = query[0].reference
            chat_doc = query[0]
            encontrado_por_evento = True
        else:
            return jsonify({"erro": "Chat não encontrado"}), 404

    chat_data = chat_doc.to_dict()
    user_adm = chat_data.get("user_adm")
    lista_participantes = chat_data.get("participantes", [])

    novos_participantes = [p for p in novos_participantes if p not in lista_participantes]
    lista_participantes += novos_participantes

    if not encontrado_por_evento and usuario_id != user_adm:
        return jsonify({"erro": "Apenas o administrador do chat pode adicionar participantes."}), 403

    chat_ref.update({"participantes": lista_participantes})

    return jsonify({
        "mensagem": "Participantes adicionados com sucesso",
        "chat_id": chat_ref.id,
        "modo_busca": "id_evento" if encontrado_por_evento else "id_chat"
    }), 200

@token_required
def remover_do_chat(chat_id, usuarios_remover):
    usuario_id = g.user_id
    chats_ref = db.collection("Chat")
    encontrado_por_evento = False

    try:
        chat_ref = chats_ref.document(chat_id)
        chat_doc = chat_ref.get()

        if not chat_doc.exists:
            query = chats_ref.where("id_evento", "==", chat_id).limit(1).get()
            if query:
                chat_ref = query[0].reference
                chat_doc = query[0]
                encontrado_por_evento = True
            else:
                return jsonify({"erro": "Chat não encontrado"}), 404

        chat_data = chat_doc.to_dict()
        user_adm = chat_data.get("user_adm")
        lista_participantes = chat_data.get("participantes", [])

        if [usuario_id] == usuarios_remover or user_adm == usuario_id:
            return jsonify({"erro": "Você não tem permissão para remover este(s) usuário(s)."}), 403

        lista_participantes = [p for p in lista_participantes if p not in usuarios_remover]
        chat_ref.update({"participantes": lista_participantes})

        if not lista_participantes:
            chat_ref.delete()
            return jsonify({
                "mensagem": "Todos os participantes foram removidos. Chat deletado.",
                "modo_busca": "id_evento" if encontrado_por_evento else "id_chat"
            }), 200

        return jsonify({
            "mensagem": "Participante(s) removido(s) com sucesso.",
            "modo_busca": "id_evento" if encontrado_por_evento else "id_chat"
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao remover participante(s): {str(e)}"}), 500

    

#testado 
@token_required
def mudar_nome_chat(chat_id,nome_novo):
    usuario_id = g.user_id
    chat_ref = db.collection("Chat").document(chat_id)
    chat_doc = chat_ref.get()
    chat_data = chat_doc.to_dict()
    user_adm = chat_data.get("user_adm")
    if user_adm == usuario_id:
        chat_ref.update({"nome_chat": nome_novo})
        return {"mensagem": "Nome do chat atualizado com sucesso"}, 200
    else:
        return {"erro": "Você não tem permissão para mudar o nome do grupo."}, 403

#testado
@token_required
def mandar_mensagem(chat_id, texto_mensagem):
    usuario_id = g.user_id
    chat_ref = db.collection("Chat").document(chat_id)
    chat_doc = chat_ref.get()

    if not chat_doc.exists:
        return {"erro": "Chat não encontrado."}, 404

    chat_data = chat_doc.to_dict()

    lista_participantes = chat_data.get("participantes", [])
    if usuario_id not in lista_participantes:
        return {"erro": "Você não é participante deste chat e não pode enviar mensagens."}, 403

    timestamp_atual = firestore.SERVER_TIMESTAMP 

    usuario_ref = db.collection("Usuarios").document(usuario_id)
    usuarios_doc = usuario_ref.get()
    usuario_data = usuarios_doc.to_dict()
    foto_usuario = usuario_data.get('foto_perfil')
    nome_usuario = usuario_data.get('username')

    nova_mensagem = {
        "id_mensagem": str(uuid.uuid4()),
        "id_remetente": usuario_id,
        "texto": texto_mensagem,
        "timestamp": timestamp_atual,
        "foto_usuario": foto_usuario,
        "nome_usuario": nome_usuario
    }

    try:
        chat_ref.collection("mensagens").add(nova_mensagem)

        chat_ref.update({"ultima_mensagem": texto_mensagem,"horario_ultima_mensagem": timestamp_atual})
        
        return {"mensagem": "Mensagem enviada com sucesso!"}, 201

    except Exception as e:
        return {"erro": f"Erro ao enviar mensagem: {str(e)}"}, 500

@token_required
def deletar_chat(id):
    usuario_id = g.user_id
    chats_ref = db.collection("Chat")
    try:
        chat_ref = chats_ref.document(id)
        chat_doc = chat_ref.get()
        encontrado_por_evento = False

        if not chat_doc.exists:
            query = chats_ref.where("id_evento", "==", id).limit(1).get()
            if query:
                chat_ref = query[0].reference
                chat_doc = query[0]
                encontrado_por_evento = True
            else:
                return jsonify({"erro": "Chat não encontrado"}), 404

        chat_data = chat_doc.to_dict()
        user_adm = chat_data.get("user_adm")

        if usuario_id != user_adm:
            return jsonify({"mensagem": "Você não tem permissão para apagar este chat"}), 403

        chat_ref.delete()

        return jsonify({
            "mensagem": "Chat deletado com sucesso!",
            "modo_busca": "id_evento" if encontrado_por_evento else "id_chat"
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao deletar chat: {str(e)}"}), 500

@token_required
def exibir_chats():
    usuario_id = g.user_id
    try:
        chats_ref = (
            db.collection("Chat")
            .where("participantes", "array_contains", usuario_id)
            .order_by("horario_ultima_mensagem", direction=firestore.Query.DESCENDING))
        chats_docs = chats_ref.get()
        chats = []
        for doc in chats_docs:
            dados = doc.to_dict()
            ultima_visualizacao = dados.get("ultima_visualizacao_por_usuario", {}).get(usuario_id)
            mensagens_nao_lidas = 0       
            if ultima_visualizacao:
                    mensagens_ref = db.collection("Chat").document(doc.id).collection("mensagens")
                    consulta_nao_lidas = mensagens_ref.where("timestamp", ">", ultima_visualizacao)
                    mensagens_nao_lidas = len(list(consulta_nao_lidas.stream()))
                    chats.append({
                    "id_chat": doc.id,
                    "nome_chat": dados.get("nome_chat"),
                    "ultima_mensagem": dados.get("ultima_mensagem"),
                    "horario_ultima_mensagem": dados.get("horario_ultima_mensagem"),
                    "mensagens_nao_lidas": mensagens_nao_lidas,
                    "foto_chat":dados.get("foto_chat")
                    })
        return jsonify(chats), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar chats: {str(e)}"}), 500


@token_required
def exibir_conversa(chat_id):
    usuario_id = g.user_id
    chat_ref = db.collection("Chat").document(chat_id)

    try:
        chat_doc = chat_ref.get()
        if not chat_doc.exists:
            return jsonify({"erro": "Chat não encontrado."}), 404

        chat_data = chat_doc.to_dict()
        if usuario_id not in chat_data.get("participantes", []):
            return jsonify({"erro": "Você não faz parte deste chat."}), 403

        mensagens_ref = (
            chat_ref
            .collection("mensagens")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        mensagens_docs = mensagens_ref.get()

        mensagens = []
        for doc in mensagens_docs:
            dados = doc.to_dict()
            mensagens.append({
                "mensagem_id": doc.id,
                "id_remetente": dados.get("id_remetente"),
                "texto": dados.get("texto"),
                "timestamp": dados.get("timestamp"),
                "foto_usuario":  dados.get("foto_usuario"),
                "nome_usuario":  dados.get("nome_usuario")

            })
        timestamp_atual = firestore.SERVER_TIMESTAMP
        chat_ref.update({f"ultima_visualizacao_por_usuario.{usuario_id}": timestamp_atual})

        return jsonify(mensagens), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar mensagens: {str(e)}"}), 500