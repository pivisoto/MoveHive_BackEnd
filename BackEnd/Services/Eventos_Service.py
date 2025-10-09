import uuid
from datetime import datetime, timezone
from flask import g, request 
from Models.Notificacao_Model import Notificacao
from Services.Notificacao_Service import criar_notificacao
from Models.Eventos_Model import Evento
from firebase_admin import firestore, credentials
import firebase_admin
from flask import g
from google.cloud.firestore_v1 import ArrayUnion
from datetime import datetime
from Models.Eventos_Model import Evento  
from datetime import datetime
import uuid
from firebase_admin import firestore, credentials, storage
from google.cloud.firestore import ArrayUnion
from flask import g, jsonify
from Models.Treino_Model import Treinos
from middlewares.auth_token import token_required
import firebase_admin


bucket = storage.bucket()
db = firestore.client()

# Implementado
@token_required
def adicionar_evento(titulo, descricao, esporte_nome, data_hora_str, endereco, localizacao,
                    torneio=False, premiacao=0, link_oficial=None, arquivo_foto=None):
    
    usuario_id = g.user_id

    user_ref = db.collection('UsuariosEmpresa').document(usuario_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return {"erro": "Permissão negada. Somente empresas podem criar eventos."}, 200

    esportes_ref = db.collection('Esportes')
    esporte_query = esportes_ref.where('nome', '==', esporte_nome).limit(1).stream()
    esporte_doc = next(esporte_query, None)

    if esporte_doc is None:
        return {"erro": f"Esporte '{esporte_nome}' não encontrado."}, 404

    try:
        data_hora = datetime.strptime(data_hora_str, "%Y-%m-%dT%H:%M:%S")
        data_hora = data_hora.replace(tzinfo=timezone.utc)  
        agora = datetime.now(timezone.utc)
    
        if data_hora <= agora:
            return {"erro": "A data e hora do evento devem ser no futuro."}, 400

    except ValueError:
        return {"erro": "Formato de data_hora inválido. Use: YYYY-MM-DDTHH:MM:SS"}, 400

    evento = Evento(
        usuario_id=usuario_id,
        titulo=titulo,
        descricao=descricao,
        esporte_nome=esporte_nome,
        localizacao=localizacao,
        endereco=endereco,
        data_hora=data_hora,
        torneio=torneio,
        premiacao=premiacao,
        foto=None,  
        link_oficial=link_oficial,
        interesse=[],
        status="Inscricoes_abertas"
    )

    # Upload da imagem
    if arquivo_foto:
        caminho = f"UsuariosEmpresa/{usuario_id}/Fotos/evento_{evento.id}.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(arquivo_foto, content_type=arquivo_foto.content_type)
        blob.make_public()
        evento.foto = blob.public_url

    eventos_ref = db.collection('Eventos')
    eventos_ref.document(evento.id).set(evento.to_dict())

    user_ref.update({
        'eventos_criados': ArrayUnion([evento.id])
    })

    return evento.to_dict(), 201



# Implementado
@token_required
def listar_eventos_usuario():
    usuario_id = g.user_id

    eventos_ref = db.collection('Eventos')
    eventos_query = eventos_ref.where('usuario_id', '==', usuario_id).stream()

    eventos = []
    for doc in eventos_query:
        evento_data = doc.to_dict()
        evento_data['id'] = doc.id
        eventos.append(evento_data)

    return jsonify(eventos), 200


# Implementado
@token_required
def listar_eventos_por_id_usuario(usuario_id):
   
    try:
        eventos_ref = db.collection('Eventos')
        
        eventos_query = eventos_ref.where('usuario_id', '==', usuario_id).stream()

        eventos = []
        for doc in eventos_query:
            evento_data = doc.to_dict()
            evento_data['id'] = doc.id  
            eventos.append(evento_data)


        if not eventos:
            return jsonify({"mensagem": "Nenhum evento encontrado para este usuário."}), 404

        return jsonify(eventos), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500



# Implementado
@token_required
def editar_evento_por_id(evento_id, dados, imagem=None):
    usuario_id = g.user_id
    evento_ref = db.collection('Eventos').document(evento_id)
    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()
    if evento_data.get('usuario_id') != usuario_id:
        return {"erro": "Permissão negada para editar este evento."}, 403

    updates = {}
    for campo, valor in dados.items():
        if valor is not None:
            try:
                if campo == 'data_hora':
                    updates[campo] = datetime.strptime(valor, "%Y-%m-%dT%H:%M:%S")
                elif campo in ['torneio']:
                    updates[campo] = valor.lower() == 'true'
                elif campo == 'premiacao':
                    updates[campo] = float(valor)
                else:
                    updates[campo] = valor
            except ValueError:
                return {"erro": f"Valor inválido para o campo '{campo}'."}, 400

    if imagem:
        try:
            caminho = f"UsuariosEmpresa/{usuario_id}/Fotos/evento_{evento_id}.jpg"
            blob = bucket.blob(caminho)

            import time
            imagem.seek(0)
            blob.upload_from_file(imagem, content_type=imagem.content_type)
            blob.make_public()

            timestamp = int(time.time())
            updates['foto'] = f"{blob.public_url}?v={timestamp}"

        except Exception as e:
            return {"erro": f"Erro ao fazer upload da imagem: {str(e)}"}, 500

    if not updates:
        return {"mensagem": "Nenhuma alteração foi feita."}, 200

    evento_ref.update(updates)
    return {"mensagem": "Evento atualizado com sucesso."}, 200



# Implementado
@token_required
def deletar_evento(evento_id):
    usuario_id = g.user_id

    user_ref = db.collection('UsuariosEmpresa').document(usuario_id)
    evento_ref = db.collection('Eventos').document(evento_id)
    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()

    if evento_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para excluir este evento."}, 403

    try:
        caminho = f"UsuariosEmpresa/{usuario_id}/Fotos/evento_{evento_id}.jpg"
        blob = bucket.blob(caminho)
        if blob.exists():
            blob.delete()
            print(f"Imagem {caminho} excluída do Storage.")
        else:
            print(f"Nenhuma imagem encontrada em {caminho} para excluir.")
    except Exception as e:
        print(f"Erro ao excluir a imagem: {e}")

    try:
        usuarios_ref = db.collection('Usuarios')
        usuarios = usuarios_ref.stream()

        for doc in usuarios:
            dados_usuario = doc.to_dict()
            if 'interesses' in dados_usuario and evento_id in dados_usuario['interesses']:
                doc.reference.update({
                    'interesses': firestore.ArrayRemove([evento_id])
                })
                print(f"Removido evento {evento_id} da lista de interesse do usuário {doc.id}")
    except Exception as e:
        print(f"Erro ao remover o evento das listas de interesse: {e}")

    evento_ref.delete()

    user_ref.update({
        'eventos_criados': firestore.ArrayRemove([evento_id])
    })

    return {"mensagem": "Evento excluído com sucesso."}, 200


# Implementado
@token_required
def listar_eventos():
    usuario_id = g.user_id  

    eventos_ref = db.collection('Eventos')
    query = eventos_ref.where('torneio', '==', False)
    eventos = query.stream()

    lista_eventos = []
    for doc in eventos:
        evento = doc.to_dict()
        evento['id'] = doc.id
        lista_eventos.append(evento)

    return jsonify(lista_eventos), 200



# Implementado
@token_required
def listar_torneios():
    usuario_id = g.user_id  

    eventos_ref = db.collection('Eventos')
    query = eventos_ref.where('torneio', '==', True)
    eventos = query.stream()

    lista_eventos = []
    for doc in eventos:
        evento = doc.to_dict()
        evento['id'] = doc.id
        lista_eventos.append(evento)

    return jsonify(lista_eventos), 200
 

@token_required
def listar_eventos_interesse():
    usuario_id = g.user_id  

    try:
        user_ref = db.collection('Usuarios').document(usuario_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return {"erro": "Usuário não encontrado."}, 404

        user_data = user_doc.to_dict()
        eventos_ids = user_data.get('interesses', [])

        if not eventos_ids:
            return jsonify({"mensagem": "Você não está interessado em nenhum evento ou torneio."}), 200

        eventos_ref = db.collection('Eventos')
        eventos = []
        for evento_id in eventos_ids:
            evento_doc = eventos_ref.document(evento_id).get()
            if evento_doc.exists:
                evento_data = evento_doc.to_dict()
                evento_data['id'] = evento_doc.id
                eventos.append(evento_data)

        return jsonify(eventos), 200

    except Exception as e:
        return {"erro": f"Erro ao listar eventos interessados: {str(e)}"}, 500
    

# Implementado
@token_required
def tenho_interesse_evento(evento_id):
    usuario_id = g.user_id

    evento_ref = db.collection('Eventos').document(evento_id)
    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()

    participantes = evento_data.get("interesse", [])

    if usuario_id in participantes:
        return {"erro": "Você já demonstrou interesse a esse Evento."}, 400


    evento_ref.update({
        'interesse': ArrayUnion([usuario_id])
    })


    user_ref = db.collection('Usuarios').document(usuario_id)
    user_ref.update({
        'interesses': ArrayUnion([evento_id])
    })


    return {"mensagem": "Interesse mostrado para o evento."}, 200

            

# Implementado
@token_required
def cancelar_interesse_evento(evento_id):
    usuario_id = g.user_id

    evento_ref = db.collection('Eventos').document(evento_id)
    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()
    interessados = evento_data.get("interesse", [])

    if usuario_id not in interessados:
        return {"erro": "Você não demonstrou interesse nesse evento."}, 400

    try:
        evento_ref.update({
            'interesse': firestore.ArrayRemove([usuario_id])
        })

        user_ref = db.collection('Usuarios').document(usuario_id)
        user_ref.update({
            'interesses': firestore.ArrayRemove([evento_id])
        })

        return {"mensagem": "Interesse cancelada com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao cancelar interesse: {str(e)}"}, 500
