from datetime import datetime, timezone
import uuid
from firebase_admin import firestore, credentials, storage
from flask import g
from Models.Notificacao_Model import Notificacao
from middlewares.auth_token import token_required
import firebase_admin

db = firestore.client()
bucket = storage.bucket()


# Implementado
#@token_required
def criar_notificacao(usuario_destino_id, tipo, referencia_id, mensagem):
    #usuario_origem_id = g.user_id
    usuario_origem_id = "a17db146-e5fa-4b21-aa7d-b3e405d7e75d"
    user_ref = db.collection('Usuarios').document(usuario_destino_id)
    if not user_ref.get().exists:
        return {"erro": "Usuário destino não encontrado."}, 404
    notificacao = Notificacao(
        usuario_destino_id=usuario_destino_id,
        usuario_origem_id=usuario_origem_id,
        tipo=tipo,
        referencia_id=referencia_id,
        mensagem=mensagem
    )
    notificacoes_ref = db.collection('Notificacoes')
    notificacoes_ref.document(notificacao.id).set(notificacao.to_dict())
    return notificacao.to_dict(), 201


# Implementada
@token_required
def pegar_notificacoes():

    usuario_id = g.user_id
    notificacoes_ref = db.collection('Notificacoes')

    query = (
        notificacoes_ref
        .where('usuario_destino_id', '==', usuario_id)
        .order_by('data_criacao', direction=firestore.Query.DESCENDING)
        .stream()
    )

    notificacoes = [doc.to_dict() for doc in query]

    return notificacoes, 200

# Implementada
@token_required
def marcar_notificacao_lida(notificacao_id):
    usuario_id = g.user_id
    notificacao_ref = db.collection("Notificacoes").document(notificacao_id)
    notificacao_doc = notificacao_ref.get()

    if not notificacao_doc.exists:
        return {"erro": "Notificação não encontrada."}, 404

    notificacao_data = notificacao_doc.to_dict()

    if notificacao_data.get("usuario_destino_id") != usuario_id:
        return {"erro": "Você não tem permissão para alterar essa notificação."}, 403

    notificacao_ref.update({"lida": True})

    return {"mensagem": "Notificação marcada como lida com sucesso."}, 200


# Implementada
@token_required
def deletar_notificacao(notificacao_id):
    try:
        usuario_id = g.user_id  
        notificacao_ref = db.collection("Notificacoes").document(notificacao_id)
        notificacao_doc = notificacao_ref.get()

        if not notificacao_doc.exists:
            return {"erro": "Notificação não encontrada."}

        notificacao_data = notificacao_doc.to_dict()
        
        # Verifica se o usuário é o destinatário
        if notificacao_data.get("usuario_destino_id") != usuario_id:
            return {"erro": "Você não tem permissão para deletar esta notificação."}, 403

        notificacao_ref.delete()
        return {"mensagem": "Notificação deletada com sucesso."}

    except Exception as e:
        return {"erro": f"Erro ao deletar notificação: {str(e)}"}