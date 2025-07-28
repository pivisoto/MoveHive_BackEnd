import uuid
from datetime import datetime, timezone
from flask import g, request 
from Models.Eventos_Model import Evento
from firebase_admin import firestore, credentials
import firebase_admin
from flask import g
from google.cloud.firestore_v1 import ArrayUnion
from datetime import datetime
from Models.Eventos_Model import Evento  # ajuste o caminho se necessário
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


@token_required
def adicionar_evento(titulo, descricao, esporte_nome, data_hora_str, localizacao,
                     max_participantes, torneio=False, premiacao=0, privado=False,
                     observacoes=None, arquivo_foto=None):
    
    usuario_id = g.user_id
    user_ref = db.collection('Usuarios').document(usuario_id)

    # Buscar esporte
    esportes_ref = db.collection('Esportes')
    esporte_query = esportes_ref.where('nome', '==', esporte_nome).limit(1).stream()
    esporte_doc = next(esporte_query, None)

    if esporte_doc is None:
        return {"erro": f"Esporte '{esporte_nome}' não encontrado."}, 404

    try:
        data_hora = datetime.strptime(data_hora_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return {"erro": "Formato de data_hora inválido. Use: YYYY-MM-DDTHH:MM:SS"}, 400

    if max_participantes <= 0:
        return {"erro": "Número máximo de participantes deve ser positivo."}, 400

    evento = Evento(
        usuario_id=usuario_id,
        titulo=titulo,
        descricao=descricao,
        esporte_nome=esporte_nome,
        localizacao=localizacao,
        data_hora=data_hora,
        max_participantes=max_participantes,
        torneio=torneio,
        premiacao=premiacao,
        foto=None,  
        participantes=[],
        privado=privado,
        observacoes=observacoes
    )

    # Upload da imagem
    if arquivo_foto:
        caminho = f"Usuarios/{usuario_id}/Fotos/evento_{evento.id}.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(arquivo_foto, content_type=arquivo_foto.content_type)
        blob.make_public()
        evento.foto = blob.public_url

    eventos_ref = db.collection('Eventos')
    eventos_ref.document(evento.id).set(evento.to_dict())

    # Atualizar referência do usuário com o novo evento
    user_ref.update({
        'eventos_criados': ArrayUnion([evento.id])
    })

    return evento.to_dict(), 201


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
                elif campo in ['torneio', 'privado']:
                    updates[campo] = valor.lower() == 'true'
                elif campo == 'max_participantes':
                    valor_int = int(valor)
                    if valor_int <= 0:
                        return {"erro": "max_participantes deve ser maior que zero."}, 400
                    updates[campo] = valor_int
                elif campo == 'premiacao':
                    updates[campo] = float(valor)
                else:
                    updates[campo] = valor
            except ValueError:
                return {"erro": f"Valor inválido para o campo '{campo}'."}, 400

    if imagem:
        try:
            caminho = f"Usuarios/{usuario_id}/Fotos/evento_{evento_id}.jpg"
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


@token_required
def deletar_evento(evento_id):
    usuario_id = g.user_id

    user_ref = db.collection('Usuarios').document(usuario_id)
    evento_ref = db.collection('Eventos').document(evento_id)

    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()

    if evento_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para excluir este evento."}, 403

    try:
        caminho = f"Usuarios/{usuario_id}/Fotos/evento_{evento_id}.jpg"
        blob = bucket.blob(caminho)
        if blob.exists():
            blob.delete()
            print(f"Imagem {caminho} excluída do Storage.")
        else:
            print(f"Nenhuma imagem encontrada em {caminho} para excluir.")
    except Exception as e:
        print(f"Erro ao excluir a imagem: {e}")

    evento_ref.delete()

    user_ref.update({
        'eventos_criados': firestore.ArrayRemove([evento_id])
    })

    return {"mensagem": "Evento excluído com sucesso."}, 200
