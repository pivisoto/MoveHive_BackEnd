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



# Implementado
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
        # Excluir imagem do Storage, se existir
        caminho = f"Usuarios/{usuario_id}/Fotos/evento_{evento_id}.jpg"
        blob = bucket.blob(caminho)
        if blob.exists():
            blob.delete()
            print(f"Imagem {caminho} excluída do Storage.")
        else:
            print(f"Nenhuma imagem encontrada em {caminho} para excluir.")
    except Exception as e:
        print(f"Erro ao excluir a imagem: {e}")

    try:
        # Remover o evento do campo "eventos_participando" de cada usuário participante
        participantes = evento_data.get('participantes', [])
        for participante_id in participantes:
            participante_ref = db.collection('Usuarios').document(participante_id)
            participante_ref.update({
                'eventos_participando': firestore.ArrayRemove([evento_id])
            })

        # Deletar o evento
        evento_ref.delete()

        # Remover o evento da lista de eventos criados pelo usuário
        user_ref.update({
            'eventos_criados': firestore.ArrayRemove([evento_id])
        })

        return {"mensagem": "Evento excluído com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao excluir o evento: {str(e)}"}, 500



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



# Implementado
@token_required
def participar_evento(evento_id):
    usuario_id = g.user_id

    evento_ref = db.collection('Eventos').document(evento_id)
    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()
    dono_evento_id = evento_data.get("usuario_id")
    privado = evento_data.get("privado", False)

    if dono_evento_id == usuario_id:
        return {"erro": "Você é o criador deste evento e já está participando."}, 400

    participantes = evento_data.get("participantes", [])
    pendentes = evento_data.get("pendentes", [])

    if usuario_id in participantes:
        return {"erro": "Você já está participando deste evento."}, 400
    
    if usuario_id in pendentes:
        return {"erro": "Você já solicitou participação e está aguardando aprovação."}, 400

    max_participantes = evento_data.get("max_participantes", 0)
    if len(participantes) >= max_participantes:
        return {"erro": "Limite de participantes atingido."}, 400

    try:
        if privado:
            evento_ref.update({
                'pendentes': ArrayUnion([usuario_id])
            })

            user_ref = db.collection('Usuarios').document(usuario_id)
            user_ref.update({
                'eventos_pendentes': ArrayUnion([evento_id])
            })

            return {"mensagem": "Solicitação enviada! Aguarde aprovação do dono do evento."}, 200

        else:
            evento_ref.update({
                'participantes': ArrayUnion([usuario_id])
            })

            user_ref = db.collection('Usuarios').document(usuario_id)
            user_ref.update({
                'eventos_participando': ArrayUnion([evento_id])
            })

            usuario_doc = user_ref.get()
            usuario_nome = usuario_doc.to_dict().get("username", "Alguém")
            titulo_evento = evento_data.get('titulo', 'sem título')

            mensagem = f"{usuario_nome} está participando do seu evento '{titulo_evento}'"
            tipo = "participacao_evento"
            referencia_id = evento_id

            criar_notificacao(
                usuario_destino_id=dono_evento_id,
                tipo=tipo,
                referencia_id=referencia_id,
                mensagem=mensagem
            )

            return {"mensagem": "Participação confirmada com sucesso!"}, 200

    except Exception as e:
        return {"erro": f"Erro ao participar do evento: {str(e)}"}, 500



# Implementado
@token_required
def cancelar_participacao(evento_id):
    usuario_id = g.user_id

    evento_ref = db.collection('Eventos').document(evento_id)
    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()
    participantes = evento_data.get("participantes", [])

    if usuario_id not in participantes:
        return {"erro": "Você não está participando deste evento."}, 400

    if evento_data.get("usuario_id") == usuario_id:
        return {"erro": "O criador do evento não pode cancelar a própria participação."}, 400

    try:
        evento_ref.update({
            'participantes': firestore.ArrayRemove([usuario_id])
        })

        user_ref = db.collection('Usuarios').document(usuario_id)
        user_ref.update({
            'eventos_participando': firestore.ArrayRemove([evento_id])
        })

        return {"mensagem": "Participação cancelada com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao cancelar participação: {str(e)}"}, 500
    


# Implementado
@token_required
def listar_eventos_participando():
    usuario_id = g.user_id  

    try:
        user_ref = db.collection('Usuarios').document(usuario_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return {"erro": "Usuário não encontrado."}, 404

        user_data = user_doc.to_dict()
        eventos_ids = user_data.get('eventos_participando', [])

        if not eventos_ids:
            return jsonify({"mensagem": "Você não está participando de nenhum evento ou torneio."}), 200

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
        return {"erro": f"Erro ao listar eventos participando: {str(e)}"}, 500
    

# Implementado
@token_required
def decidir_participante(evento_id, usuario_id, acao):
    usuario_dono = g.user_id
    evento_ref = db.collection("Eventos").document(evento_id)
    evento_data = evento_ref.get().to_dict()

    if evento_data["usuario_id"] != usuario_dono:
        return {"erro": "Apenas o dono pode aprovar ou recusar."}, 403

    pendentes = evento_data.get("pendentes", [])
    if usuario_id not in pendentes:
        return {"erro": "Usuário não está na lista de pendentes."}, 400

    if acao == "aceitar":
        evento_ref.update({
            "pendentes": firestore.ArrayRemove([usuario_id]),
            "participantes": ArrayUnion([usuario_id])
        })
        db.collection("Usuarios").document(usuario_id).update({
            "eventos_pendentes": firestore.ArrayRemove([evento_id]),
            "eventos_participando": ArrayUnion([evento_id])
        })
        return {"mensagem": "Usuário aceito no evento."}, 200

    elif acao == "recusar":
        evento_ref.update({
            "pendentes": firestore.ArrayRemove([usuario_id])
        })
        db.collection("Usuarios").document(usuario_id).update({
            "eventos_pendentes": firestore.ArrayRemove([evento_id])
        })
        return {"mensagem": "Usuário recusado."}, 200

    else:
        return {"erro": "Ação inválida"}, 400
    
# Implementado
@token_required
def listar_pendentes(evento_id):
    usuario_dono = g.user_id
    evento_ref = db.collection("Eventos").document(evento_id)
    evento_doc = evento_ref.get()

    if not evento_doc.exists:
        return {"erro": "Evento não encontrado."}, 404

    evento_data = evento_doc.to_dict()

    if evento_data.get("usuario_id") != usuario_dono:
        return {"erro": "Apenas o dono do evento pode ver os pendentes."}, 403

    pendentes_ids = evento_data.get("pendentes", [])
    pendentes_info = []

    for user_id in pendentes_ids:
        user_doc = db.collection("Usuarios").document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            pendentes_info.append({
                "id": user_id,
                "nome_completo": user_data.get("nome_completo"),
                "username": user_data.get("username"),
                "foto_perfil": user_data.get("foto_perfil")
            })

    return {"pendentes": pendentes_info}, 200