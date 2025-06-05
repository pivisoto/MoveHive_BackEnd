from datetime import datetime
import uuid
from firebase_admin import firestore, credentials, storage
from google.cloud.firestore import ArrayUnion
from flask import g, jsonify
from Models.Treino_Model import Treinos
from middlewares.auth_token import token_required
import firebase_admin

if not firebase_admin._apps:
    cred = credentials.Certificate("safeviewbd-firebase-adminsdk-657bv-0ff3d67904.json")
    firebase_admin.initialize_app(cred, {
    'storageBucket': 'safeviewbd.appspot.com'
})

bucket = storage.bucket()
db = firestore.client()


@token_required
def adicionar_treino(titulo, descricao, nome_esporte, data_hora_str, lugar, tempo_treinado, arquivo_imagem=None):
    usuario_id = g.user_id
    user_ref = db.collection('Usuarios').document(usuario_id)

    esportes_ref = db.collection('Esportes')
    esportes_query = esportes_ref.where('nome', '==', nome_esporte).limit(1).stream()
    esporte_doc = next(esportes_query, None)

    if esporte_doc is None:
        return {"erro": f"Esporte '{nome_esporte}' não encontrado."}, 404

    esporte_dict = esporte_doc.to_dict()
    esporte_data = {
        "id": esporte_doc.id,
        "nome": esporte_dict.get("nome"),
        "descricao": esporte_dict.get("descricao"),
        "Kcal_por_1hr": esporte_dict.get("Kcal_por_1hr", 0)
    }

    try:
        data_hora = datetime.strptime(data_hora_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return {"erro": "Formato de data_hora inválido. Use: YYYY-MM-DDTHH:MM:SS"}, 400

    if tempo_treinado <= 0:
        return {"erro": "Tempo de treino deve ser um número positivo."}, 400

    treinos_ref = db.collection('Treinos')

    treino = Treinos(
        usuario_id=usuario_id,
        titulo=titulo,
        descricao=descricao,
        esporte=esporte_data,
        data_hora=data_hora,
        lugar=lugar,
        tempo_treinado=tempo_treinado
    )

    if arquivo_imagem:
        caminho = f"Usuarios/{usuario_id}/Fotos/treino_{treino.id}.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(arquivo_imagem, content_type=arquivo_imagem.content_type)
        blob.make_public()
        treino.arquivo_imagem = blob.public_url

    treinos_ref.document(treino.id).set(treino.to_dict())

    user_ref.update({
        'treinos_id': ArrayUnion([treino.id])
    })

    user_snapshot = user_ref.get()
    if user_snapshot.exists:
        user_data = user_snapshot.to_dict()
        pontos_atuais = user_data.get('pontos', 0)
        novos_pontos = pontos_atuais + treino.pontos

        user_ref.update({
            'pontos': novos_pontos
        })

    return treino.to_dict(), 201


@token_required
def listar_treino_por_userID():
    usuario_id = g.user_id

    user_ref = db.collection('Usuarios').document(usuario_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return {"erro": "Usuário não encontrado."}, 404

    user_data = user_doc.to_dict()
    treinos_id = user_data.get('treinos_id', [])

    if not treinos_id:
        return {"mensagem": "Nenhum treino encontrado para este usuário."}, 200

    treinos_ref = db.collection('Treinos')
    treinos = []

    for treino_id in treinos_id:
        treino_doc = treinos_ref.document(treino_id).get()
        if treino_doc.exists:
            treino_data = treino_doc.to_dict()
            treino_data['id'] = treino_doc.id
            treinos.append(treino_data)

    return jsonify(treinos), 200



@token_required
def excluir_treino_por_treinoID(treino_id):
    usuario_id = g.user_id

    user_ref = db.collection('Usuarios').document(usuario_id)
    treino_ref = db.collection('Treinos').document(treino_id)

    treino_doc = treino_ref.get()

    if not treino_doc.exists:
        return {"erro": "Treino não encontrado."}, 404

    treino_data = treino_doc.to_dict()

    if treino_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para excluir este treino."}, 403

    try:
        caminho = f"Usuarios/{usuario_id}/Fotos/treino_{treino_id}.jpg"
        blob = bucket.blob(caminho)
        if blob.exists():
            blob.delete()
            print(f"Imagem {caminho} excluída do Storage.")
        else:
            print(f"Nenhuma imagem encontrada em {caminho} para excluir.")
    except Exception as e:
        print(f"Erro ao excluir a imagem: {e}")


    treino_ref.delete()

    user_ref.update({
        'treinos_id': firestore.ArrayRemove([treino_id])
    })

    user_snapshot = user_ref.get()
    if user_snapshot.exists:
        user_data = user_snapshot.to_dict()
        pontos_atuais = user_data.get('pontos', 0)
        pontos_a_remover = treino_data.get('pontos', 0)
        novos_pontos = max(pontos_atuais - pontos_a_remover, 0)  

        user_ref.update({
            'pontos': novos_pontos
        })

    return {"mensagem": "Treino excluído com sucesso."}, 200


@token_required
def atualizar_treino_por_treinoID(
    treino_id,
    titulo=None,
    descricao=None,
    nome_esporte=None,
    data_hora_str=None,
    lugar=None,
    tempo_treinado=None,
    arquivo_imagem=None
):
    usuario_id = g.user_id

    user_ref = db.collection('Usuarios').document(usuario_id)
    treino_ref = db.collection('Treinos').document(treino_id)

    treino_doc = treino_ref.get()

    if not treino_doc.exists:
        return {"erro": "Treino não encontrado."}, 404

    treino_data = treino_doc.to_dict()

    if treino_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para atualizar este treino."}, 403

    updates = {}

    if titulo is not None:
        updates['titulo'] = titulo
    if descricao is not None:
        updates['descricao'] = descricao
    if lugar is not None:
        updates['lugar'] = lugar

    # Upload da imagem (se enviada)
    if arquivo_imagem:
        try:
            caminho = f"Usuarios/{usuario_id}/Fotos/treino_{treino_id}.jpg"
            print(f"Service: Caminho do blob: {caminho}")
            blob = bucket.blob(caminho)

            import time
            arquivo_imagem.seek(0) # Boa prática

            blob.upload_from_file(arquivo_imagem, content_type=arquivo_imagem.content_type)
            blob.make_public()

            timestamp = int(time.time())
            url_para_salvar_no_firestore = f"{blob.public_url}?v={timestamp}"
           
            updates['arquivo_imagem'] = url_para_salvar_no_firestore
            print(f"Service: Imagem upada, URL pública: {blob.public_url}")
        except Exception as e:
         return {"erro": f"Erro ao fazer upload da imagem: {str(e)}"}, 500

    if data_hora_str is not None:
        try:
            data_hora = datetime.strptime(data_hora_str, "%Y-%m-%dT%H:%M:%S")
            updates['data_hora'] = data_hora
        except ValueError:
            return {"erro": "Formato de data_hora inválido. Use: YYYY-MM-DDTHH:MM:SS"}, 400

    if nome_esporte is not None:
        esportes_ref = db.collection('Esportes')
        esportes_query = esportes_ref.where('nome', '==', nome_esporte).limit(1).stream()
        esporte_doc = next(esportes_query, None)

        if esporte_doc is None:
            return {"erro": f"Esporte '{nome_esporte}' não encontrado."}, 404

        esporte_dict = esporte_doc.to_dict()
        esporte_data = {
            "id": esporte_doc.id,
            "nome": esporte_dict.get("nome"),
            "descricao": esporte_dict.get("descricao"),
            "Kcal_por_1hr": esporte_dict.get("Kcal_por_1hr", 0)
        }
        updates['esporte'] = esporte_data
    else:
        esporte_data = treino_data.get('esporte', {})

    # Verificar se tempo_treinado foi alterado para recalcular pontos
    pontos_antigos = treino_data.get('pontos', 0)
    if tempo_treinado is not None:
        try:
            tempo_treinado = float(tempo_treinado)
            if tempo_treinado <= 0:
                return {"erro": "Tempo de treino deve ser um número positivo."}, 400
            updates['tempo_treinado'] = tempo_treinado

            kcal_por_hora = updates.get('esporte', esporte_data).get('Kcal_por_1hr', 0)
            novos_pontos = round((tempo_treinado / 60) * kcal_por_hora)
            updates['pontos'] = novos_pontos
        except ValueError:
            return {"erro": "O tempo treinado deve ser um número válido."}, 400
    else:
        novos_pontos = pontos_antigos

    # Atualiza treino no Firestore
    treino_ref.update(updates)

    # Atualiza os pontos do usuário
    user_snapshot = user_ref.get()
    if user_snapshot.exists:
        user_data = user_snapshot.to_dict()
        pontos_atuais = user_data.get('pontos', 0)

        # Subtrai os pontos antigos e adiciona os novos
        pontos_atualizados = max(pontos_atuais - pontos_antigos + novos_pontos, 0)

        user_ref.update({
            'pontos': pontos_atualizados
        })

    treino_atualizado = treino_ref.get().to_dict()
    treino_atualizado['id'] = treino_id

    return treino_atualizado, 200


@token_required
def listar_treino_por_treinoID(treino_id):
    usuario_id = g.user_id

    treino_ref = db.collection('Treinos').document(treino_id)
    treino_doc = treino_ref.get()

    if not treino_doc.exists:
        return {"erro": "Treino não encontrado."}, 404

    treino_data = treino_doc.to_dict()

    if treino_data.get('usuario_id') != usuario_id:
        return {"erro": "Você não tem permissão para acessar este treino."}, 403

    treino_data['id'] = treino_doc.id

    return treino_data, 200