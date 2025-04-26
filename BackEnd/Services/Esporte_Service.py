from firebase_admin import firestore, credentials
from Models.Esporte_Model import Esporte
import firebase_admin

if not firebase_admin._apps:
    cred = credentials.Certificate("move-hive-firebase-adminsdk-fbsvc-0334323fd4.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Adicionar esporte
def adicionar_esporte(nome, descricao):
    esportes_ref = db.collection('Esportes')

    esporte = Esporte(nome=nome, descricao=descricao)

    doc_ref = esportes_ref.document(esporte.id)

    doc_ref.set(esporte.to_dict())
    
    return {"status": "sucesso", "id": esporte.id}, 201


# Listar todos os esportes
def listar_esportes():
    esportes_ref = db.collection('Esportes').stream()
    return [doc.to_dict() for doc in esportes_ref]



# Atualizar esporte
def atualizar_esporte(id, nome=None, descricao=None):
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



# Excluir esporte
def excluir_esporte(id):
    doc_ref = db.collection('Esportes').document(id)
    if not doc_ref.get().exists:
        return {"erro": "Esporte não encontrado"}, 404

    doc_ref.delete()
    return {"status": "sucesso", "mensagem": "Esporte excluído com sucesso"}
