import uuid
from datetime import datetime, timezone
from flask import g, request 
from Models.Notificacao_Model import Notificacao
from Services.Notificacao_Service import criar_notificacao
from Models.Hive_Model import Hive
from firebase_admin import firestore, credentials
import firebase_admin
from flask import g
from google.cloud.firestore_v1 import ArrayUnion
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
def adicionar_hive(titulo, descricao, esporte_nome, data_hora_str, endereco, localizacao,
                     max_participantes, privado=False,
                     observacoes=None, arquivo_foto=None):
    
    usuario_id = g.user_id
    user_ref = db.collection('Usuarios').document(usuario_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        empresa_ref = db.collection('UsuariosEmpresa').document(usuario_id)
        empresa_doc = empresa_ref.get()
        if empresa_doc.exists:
            return {"erro": "Usuários empresa não têm permissão para criar Hives."}, 403
        else:
            return {"erro": "Usuário não encontrado."}, 404


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
            return {"erro": "A data e hora do hive devem ser no futuro."}, 400

    except ValueError:
        return {"erro": "Formato de data_hora inválido. Use: YYYY-MM-DDTHH:MM:SS"}, 400

    if max_participantes <= 0:
        return {"erro": "Número máximo de participantes deve ser positivo."}, 400

    hive = Hive(
        usuario_id=usuario_id,
        titulo=titulo,
        descricao=descricao,
        esporte_nome=esporte_nome,
        localizacao=localizacao,
        endereco=endereco,
        data_hora=data_hora,
        max_participantes=max_participantes,
        foto=None,
        participantes=[usuario_id],
        privado=privado,
        observacoes=observacoes,
        status="Aberto"
    )

    if arquivo_foto:
        caminho = f"Usuarios/{usuario_id}/Fotos/hive_{hive.id}.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(arquivo_foto, content_type=arquivo_foto.content_type)
        blob.make_public()
        hive.foto = blob.public_url

    hive_ref = db.collection('Hive')
    hive_ref.document(hive.id).set(hive.to_dict())

    user_ref.update({
        'hive_criados': ArrayUnion([hive.id])
    })

    return hive.to_dict(), 201


# Implementado
@token_required
def listar_MeusHive():
    usuario_id = g.user_id
    try:
        hive_ref = db.collection('Hive')
        
        hive_query = hive_ref.where('usuario_id', '==', usuario_id).stream()

        hive = []
        for doc in hive_query:
            hive_data = doc.to_dict()
            hive_data['id'] = doc.id  
            hive.append(hive_data)


        if not hive:
            return jsonify({"mensagem": "Nenhum hive encontrado para este usuário."}), 404

        return jsonify(hive), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# Implementado
@token_required
def editar_hive_por_id(hive_id, dados, imagem=None):
    usuario_id = g.user_id
    hive_ref = db.collection('Hive').document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()
    if hive_data.get('usuario_id') != usuario_id:
        return {"erro": "Permissão negada para editar este hive."}, 403

    updates = {}
    for campo, valor in dados.items():
        if valor is not None:
            try:
                if campo == 'data_hora':
                    updates[campo] = datetime.strptime(valor, "%Y-%m-%dT%H:%M:%S")
                elif campo == 'max_participantes':
                    valor_int = int(valor)
                    if valor_int <= 0:
                        return {"erro": "max_participantes deve ser maior que zero."}, 400
                    updates[campo] = valor_int
                else:
                    updates[campo] = valor
            except ValueError:
                return {"erro": f"Valor inválido para o campo '{campo}'."}, 400

    if imagem:
        try:
            caminho = f"Usuarios/{usuario_id}/Fotos/hive_{hive_id}.jpg"
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

    hive_ref.update(updates)
    return {"mensagem": "hive atualizado com sucesso."}, 200


# Implementado
@token_required
def deletar_hive(hive_id):
    usuario_id = g.user_id

    user_ref = db.collection('Usuarios').document(usuario_id)
    hive_ref = db.collection('Hive').document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()

    if hive_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para excluir este hive."}, 403

    try:
        caminho = f"Usuarios/{usuario_id}/Fotos/hive_{hive_id}.jpg"
        blob = bucket.blob(caminho)
        if blob.exists():
            blob.delete()
            print(f"Imagem {caminho} excluída do Storage.")
        else:
            print(f"Nenhuma imagem encontrada em {caminho} para excluir.")
    except Exception as e:
        print(f"Erro ao excluir a imagem: {e}")

    try:
        participantes = hive_data.get('participantes', [])
        for participante_id in participantes:
            participante_ref = db.collection('Usuarios').document(participante_id)
            participante_ref.update({
                'hive_participando': firestore.ArrayRemove([hive_id])
            })

        hive_ref.delete()

        user_ref.update({
            'hive_criados': firestore.ArrayRemove([hive_id])
        })

        return {"mensagem": "hive excluído com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao excluir o hive: {str(e)}"}, 500
