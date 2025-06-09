import uuid
from datetime import datetime, timezone

from flask import g 
from Models.Eventos_Model import Evento
from firebase_admin import firestore, credentials
import firebase_admin




db = firestore.client()


# Função para Adicionar Evento

def adicionar_evento(esporte_id, titulo, localizacao, data_hora: datetime, 
                     descricao, max_participantes, nivel_esporte, visibilidade
                     ):
   
    try:
        usuario_id = g.user_id
        eventos_ref = db.collection("Eventos")


        evento = Evento(
            usuario_id=usuario_id,
            esporte_id=esporte_id,
            titulo=titulo,
            localizacao=localizacao,
            data_hora=data_hora,
            descricao=descricao,
            max_participantes=max_participantes,
            nivel_esporte=nivel_esporte,
            visibilidade=visibilidade
        )

        doc_ref = eventos_ref.document(evento.id)

        doc_ref.set(evento.to_dict())

        return {"status": "sucesso", "id": evento.id}, 201

    except Exception as e:
        print(f"Erro ao adicionar evento: {e}")
        return {"status": "erro", "mensagem": f"Não foi possível adicionar o evento: {e}"}, 500



# Função para Listar Eventos
def listar_eventos():
    try:
        eventos_ref = db.collection("Eventos").stream()
        return [doc.to_dict() for doc in eventos_ref]

    except Exception as e:
        print(f"Erro ao listar eventos: {e}")
        return [] 


# Função para Buscar Evento por ID
def buscar_evento_por_id(evento_id: str):
    try:
        doc_ref = db.collection("Eventos").document(evento_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {"erro": "Evento não encontrado"}, 404

        return doc.to_dict(), 200

    except Exception as e:
        print(f"Erro ao buscar evento {evento_id}: {e}")
        return {"status": "erro", "mensagem": f"Não foi possível buscar o evento: {e}"}, 500


# Função para Atualizar Evento
def atualizar_evento(evento_id: str,  esporte_id: str = None,
                     nome: str = None, localizacao: str = None,
                     data_hora: datetime = None, descricao: str = None,
                     max_participantes: int = None, status_evento: str = None,
                     nivel_esporte: str = None, link_oficial: str = None,
                     tipo_evento: str = None, inscricoes_ativas: bool = None,
                     participantes: list = None):

   
    try:
        doc_ref = db.collection("Eventos").document(evento_id)
        doc = doc_ref.get()

        if not doc.exists:
            return {"erro": "Evento não encontrado"}, 404

        updates = {}
        if esporte_id is not None:
            updates['esporte_id'] = esporte_id
        if nome is not None:
            updates['nome'] = nome
        if localizacao is not None:
            updates['localizacao'] = localizacao
        if data_hora is not None:
            updates['data_hora'] = data_hora
        if descricao is not None:
            updates['descricao'] = descricao
        if max_participantes is not None:
            updates['max_participantes'] = max_participantes
        if status_evento is not None:
            updates['status_evento'] = status_evento
        if nivel_esporte is not None:
            updates['nivel_esporte'] = nivel_esporte
        if link_oficial is not None:
            updates['link_oficial'] = link_oficial
        if tipo_evento is not None:
            updates['tipo_evento'] = tipo_evento
        if inscricoes_ativas is not None:
            updates['inscricoes_ativas'] = inscricoes_ativas
        if participantes is not None:
            updates['participantes'] = participantes
        if updates:
            doc_ref.update(updates)
            return {"status": "sucesso", "mensagem": "Evento atualizado com sucesso"}, 200
        else:
             return {"status": "sucesso", "mensagem": "Nenhum campo para atualizar foi fornecido"}, 200

    except Exception as e:
        print(f"Erro ao atualizar evento {evento_id}: {e}")
        return {"status": "erro", "mensagem": f"Não foi possível atualizar o evento: {e}"}, 500



# Função para Excluir evento por ID
def excluir_evento(evento_id: str):
    try:
        doc_ref = db.collection("Eventos").document(evento_id)
        if not doc_ref.get().exists:
            return {"erro": "Evento não encontrado"}, 404

        doc_ref.delete()
        return {"status": "sucesso", "mensagem": "Evento excluído com sucesso"}, 200

    except Exception as e:
        print(f"Erro ao excluir evento {evento_id}: {e}")
        return {"status": "erro", "mensagem": f"Não foi possível excluir o evento: {e}"}, 500



