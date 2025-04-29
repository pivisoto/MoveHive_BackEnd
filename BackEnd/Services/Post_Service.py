from firebase_admin import firestore, credentials
from Models.Post_Model import Postagem
import firebase_admin
import uuid
from datetime import datetime

if not firebase_admin._apps:
    cred = credentials.Certificate("move-hive-firebase-adminsdk-fbsvc-0334323fd4.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Função para Criar Postagem
def criar_postagem(usuario_id, conteudo, esporte_praticado, imagem='', status_postagem='ativo', contador_curtidas=0):

    postagem = Postagem(usuario_id=usuario_id, conteudo=conteudo, esporte_praticado=esporte_praticado, imagem=imagem, 
                        status_postagem=status_postagem, contador_curtidas=contador_curtidas)


    # Salvando no Firestore
    postagem_ref = db.collection('Postagens').document(postagem.id)
    postagem_ref.set(postagem.to_dict())


    return {"status": "sucesso", "id": postagem_ref.id}, 201



# Função para Listar Postagens
def listar_postagens():
    postagens = db.collection('Postagens').stream()
    lista = []
    for doc in postagens:
        dados = doc.to_dict()
        dados['id'] = doc.id
        lista.append(dados)
    return lista



# Função para Listar Postagens de um Usuário
def listar_postagens_por_usuario(usuario_id):
    postagens_ref = db.collection('Postagens')
    query = postagens_ref.where('usuario_id', '==', usuario_id)
    postagens = query.stream()

    lista = []
    for doc in postagens:
        dados = doc.to_dict()
        dados['id'] = doc.id
        lista.append(dados)
    
    return lista


# Função para Deletar Postagem por ID
def deletar_postagem_por_id(postagem_id):
    doc_ref = db.collection('Postagens').document(postagem_id)
    if not doc_ref.get().exists:
        return {"erro": "Postagem não encontrada"}, 404

    doc_ref.delete()
    return {"status": "sucesso", "mensagem": "Postagem deletada com sucesso"}, 200



# Função para Editar Postagem por ID
def editar_postagem_por_id(postagem_id, novos_dados):
    doc_ref = db.collection('Postagens').document(postagem_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return {"erro": "Postagem não encontrada"}, 404

    dados_atualizados = novos_dados.copy()

    doc_ref.update(dados_atualizados)
    return {"status": "sucesso", "mensagem": "Postagem atualizada com sucesso"}, 200



# Função para Curtir Postagem
def curtir_postagem(postagem_id):
    doc_ref = db.collection('Postagens').document(postagem_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return {"erro": "Postagem não encontrada"}, 404

    dados = snapshot.to_dict()
    dados['contador_curtidas'] += 1
    doc_ref.update({'contador_curtidas': dados['contador_curtidas']})

    return {"status": "sucesso", "mensagem": "Postagem curtida com sucesso", "curtidas": dados['contador_curtidas']}, 200
