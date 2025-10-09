from firebase_admin import firestore, storage
from flask import g, jsonify
from middlewares.auth_token import token_required
from Models.Chat_Model import Chat
from google.cloud.firestore import ArrayUnion
from .Notificacao_Service import criar_notificacao, deletar_notificacao
import uuid

db = firestore.client()
bucket = storage.bucket()


# Função para Criar Chat
#testado
@token_required
def criar_chat(nome_chat,lista_participantes):
    usuario_id = g.user_id
    if not lista_participantes:
        lista_participantes = []
    lista_participantes = [usuario_id] + lista_participantes
    chat = Chat(
        user_adm=usuario_id,
        nome_chat=nome_chat,
        participantes=lista_participantes,
        ultima_mensagem="Chat novo!"
    )
    db.collection('Chat').document(chat.id).set(chat.to_dict())

    return jsonify("Chat criado com sucesso"), 201

#testado
@token_required
def adicionar_ao_chat(chat_id,novos_participantes):
    usuario_id = g.user_id
    chat_ref = db.collection("Chat").document(chat_id)
    chat_doc = chat_ref.get()
    chat_data = chat_doc.to_dict()
    user_adm = chat_data.get("user_adm")
    lista_participantes = chat_data.get("participantes", [])
    novos_participantes = [item for item in novos_participantes if item not in lista_participantes]
    lista_participantes = novos_participantes + lista_participantes
    if user_adm == usuario_id:
        print(novos_participantes)
        chat_ref.update({"participantes": lista_participantes})
        return {"mensagem": "Participante(s) adicionado(s) com sucesso."}, 200
    else:
        return {"erro": "Você não tem permissão para adicionar este(s) usuário(s)."}, 403
    
#testado 
@token_required
def remover_do_chat(chat_id,usuarios_remover):
    usuario_id = g.user_id
    chat_ref = db.collection("Chat").document(chat_id)
    chat_doc = chat_ref.get()
    chat_data = chat_doc.to_dict()
    user_adm = chat_data.get("user_adm")
    lista_participantes = chat_data.get("participantes", [])
    if [usuario_id] == usuarios_remover or user_adm == usuario_id:
        lista_participantes = [item for item in lista_participantes if item not in usuarios_remover]
        chat_ref.update({"participantes": lista_participantes})
        return {"mensagem": "Participante(s) removido com sucesso."}, 200
    else:
        return {"erro": "Você não tem permissão para remover este(s) usuário(s)."}, 403
    

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


#@token_required
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

    nova_mensagem = {
        "id_remetente": usuario_id,
        "texto": texto_mensagem,
        "timestamp": timestamp_atual,
        "lida": False  
    }

    try:
        chat_ref.collection("mensagens").add(nova_mensagem)

        chat_ref.update({"ultima_mensagem": texto_mensagem,"horario_ultima_mensagem": timestamp_atual})
        
        return {"mensagem": "Mensagem enviada com sucesso!"}, 201

    except Exception as e:
        return {"erro": f"Erro ao enviar mensagem: {str(e)}"}, 500