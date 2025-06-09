from firebase_admin import firestore, credentials
from Models.Esporte_Model import Esporte
import firebase_admin



db = firestore.client()


# Função para Adicionar um Esporte
def adicionar_esporte(nome, descricao):

     try:
        esportes_ref = db.collection('Esportes')

        esporte = Esporte(nome=nome, descricao=descricao)

        doc_ref = esportes_ref.document(esporte.id)

        doc_ref.set(esporte.to_dict())
        
        return {"status": "sucesso", "id": esporte.id}, 201
     
     except Exception as e:
        print(f"Erro ao adicionar evento: {e}")
        return {"status": "erro", "mensagem": f"Não foi possível adicionar o evento: {e}"}, 500


# Função para Listar todos os esportes
def listar_esportes():
    esportes_ref = db.collection('Esportes').stream()
    return [doc.to_dict() for doc in esportes_ref]



# Função para Atualizar esporte por ID
def atualizar_esporte_por_ID(id, nome=None, descricao=None):
    doc_ref = db.collection('Esportes').document(id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"erro": "Esporte não encontrado"}, 404

    updates = {}
    if nome:
        updates['nome'] = nome
    if descricao:
        updates['descricao'] = descricao

    if updates:
        doc_ref.update(updates)

    return {"status": "sucesso", "mensagem": "Esporte atualizado com sucesso"}



# Função para Excluir esporte por ID
def excluir_esporte_por_ID(id):
    doc_ref = db.collection('Esportes').document(id)
    if not doc_ref.get().exists:
        return {"erro": "Esporte não encontrado"}, 404

    doc_ref.delete()
    return {"status": "sucesso", "mensagem": "Esporte excluído com sucesso"}
