from firebase_admin import firestore
from httplib2 import Credentials
from Models.Comentarios_Model import Comentario
import firebase_admin
import uuid
from datetime import datetime

db = firestore.client()


# Função para Criar Comentário
def criar_comentario(usuario_id, postagem_id, conteudo, status_comentario='ativo'):
    comentario = Comentario(
        usuario_id=usuario_id,
        postagem_id=postagem_id,
        conteudo=conteudo,
        status_comentario=status_comentario
    )

    # Salvando no Firestore
    comentario_ref = db.collection('Comentarios').document(comentario.id)
    comentario_ref.set(comentario.to_dict())

    return {"status": "sucesso", "id": comentario_ref.id}, 201


# Função para Listar Comentários
def listar_comentarios():
    comentarios = db.collection('Comentarios').stream()
    lista = []
    for doc in comentarios:
        dados = doc.to_dict()
        dados['id'] = doc.id
        lista.append(dados)
    return lista


# Função para Listar Comentários de uma Postagem
def listar_comentarios_por_postagem(postagem_id):
    comentarios_ref = db.collection('Comentarios')
    query = comentarios_ref.where('postagem_id', '==', postagem_id)
    comentarios = query.stream()

    lista = []
    for doc in comentarios:
        dados = doc.to_dict()
        dados['id'] = doc.id
        lista.append(dados)
    
    return lista


# Função para Listar Comentários de um Usuário
def listar_comentarios_por_usuario(usuario_id):
    comentarios_ref = db.collection('Comentarios')
    query = comentarios_ref.where('usuario_id', '==', usuario_id)
    comentarios = query.stream()

    lista = []
    for doc in comentarios:
        dados = doc.to_dict()
        dados['id'] = doc.id
        lista.append(dados)
    
    return lista


# Função para Deletar Comentário por ID
def deletar_comentario_por_id(comentario_id):
    doc_ref = db.collection('Comentarios').document(comentario_id)
    if not doc_ref.get().exists:
        return {"erro": "Comentário não encontrado"}, 404

    doc_ref.delete()
    return {"status": "sucesso", "mensagem": "Comentário deletado com sucesso"}, 200



def editar_comentario_por_id(comentario_id, novos_dados):
    doc_ref = db.collection('Comentarios').document(comentario_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return {"erro": "Comentário não encontrado"}, 404

    dados_atualizados = novos_dados.copy()
    
    campos_imutaveis = ['id', 'usuario_id', 'postagem_id', 'data_criacao']
    for campo in campos_imutaveis:
        dados_atualizados.pop(campo, None)

    doc_ref.update(dados_atualizados)
    return {"status": "sucesso", "mensagem": "Comentário atualizado com sucesso"}, 200



# Função para Alterar Status do Comentário
def alterar_status_comentario(comentario_id, novo_status):
    doc_ref = db.collection('Comentarios').document(comentario_id)
    snapshot = doc_ref.get()

    if not snapshot.exists:
        return {"erro": "Comentário não encontrado"}, 404

    if novo_status not in ['ativo', 'inativo', 'removido']:
        return {"erro": "Status inválido"}, 400

    doc_ref.update({'status_comentario': novo_status})
    return {"status": "sucesso", "mensagem": f"Status do comentário alterado para {novo_status}"}, 200