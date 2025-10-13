import uuid
from datetime import datetime, timezone
from flask import g, request 
from Models.Notificacao_Model import Notificacao
from Services.Notificacao_Service import criar_notificacao
from Services import Chat_Service 
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

    Chat_Service.criar_chat(titulo,lista_participantes=[usuario_id],id_evento=hive.id,foto_chat=hive.foto)
    
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
            return jsonify({
                "mensagem": "Nenhum hive encontrado para este usuário.",
            }), 200

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

    titulo_hive = hive_data.get('titulo', 'sem título')
    participantes = hive_data.get('participantes', [])
    pendentes = hive_data.get('pendentes', [])


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
        mensagem = f"O hive '{titulo_hive}' foi excluído pelo criador."
        tipo = "hive_excluido"

        for participante_id in participantes:
            if participante_id != usuario_id:  
                criar_notificacao(
                    usuario_destino_id=participante_id,
                    tipo=tipo,
                    referencia_id=hive_id,
                    mensagem=mensagem
                )

        for pendente_id in pendentes:
            if pendente_id != usuario_id:
                criar_notificacao(
                    usuario_destino_id=pendente_id,
                    tipo=tipo,
                    referencia_id=hive_id,
                    mensagem=mensagem
                )

        for participante_id in participantes:
            participante_ref = db.collection('Usuarios').document(participante_id)
            participante_ref.update({
                'hive_participando': firestore.ArrayRemove([hive_id])
            })


        user_ref.update({
            'hive_criados': firestore.ArrayRemove([hive_id])
        })

        Chat_Service.deletar_chat(hive_id)
        hive_ref.delete()

        return {"mensagem": f"Hive '{titulo_hive}' excluído com sucesso e participantes notificados."}, 200

    except Exception as e:
        return {"erro": f"Erro ao excluir o hive: {str(e)}"}, 500


# Implementado
@token_required
def listar_hives():

    hive_ref = db.collection('Hive')
    hive_docs = hive_ref.stream()  

    lista_hive = []
    for doc in hive_docs:
        hive = doc.to_dict()
        hive['id'] = doc.id
        lista_hive.append(hive)

    return jsonify(lista_hive), 200


# Implementado
@token_required
def participar_hive(hive_id):
    usuario_id = g.user_id

    hive_ref = db.collection('Hive').document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()
    dono_hive_id = hive_data.get("usuario_id")
    privado = hive_data.get("privado", False)

    if dono_hive_id == usuario_id:
        return {
            "mensagem": "Você é o criador deste hive e já está participando."
        }, 200


    participantes = hive_data.get("participantes", [])
    pendentes = hive_data.get("pendentes", [])

    if usuario_id in participantes:
        return {
            "mensagem": "Você já está participando deste hive."
        }, 200
    
    if usuario_id in pendentes:
        return {
            "mensagem": "Você já solicitou participação e está aguardando aprovação."
        }, 200

    max_participantes = hive_data.get("max_participantes", 0)
    if len(participantes) >= max_participantes:
        return {
            "mensagem": "Limite de participantes atingido.",
        }, 200


    try:
        user_ref = db.collection('Usuarios').document(usuario_id)
        usuario_doc = user_ref.get()
        usuario_nome = usuario_doc.to_dict().get("username", "Alguém")
        titulo_hive = hive_data.get('titulo', 'sem título')


        if privado:
            hive_ref.update({
                'pendentes': ArrayUnion([usuario_id])
            })

            user_ref.update({
                'hive_pendentes': ArrayUnion([hive_id])
            })

            mensagem = f"{usuario_nome} solicitou participar do seu hive privado '{titulo_hive}'."
            criar_notificacao(
                usuario_destino_id=dono_hive_id,
                tipo="solicitacao_hive_privado",
                referencia_id=hive_id,
                mensagem=mensagem
            )

            return {"mensagem": "Solicitação enviada! Aguarde aprovação do dono do hive."}, 200

        else:
            hive_ref.update({
                'participantes': ArrayUnion([usuario_id])
            })

            user_ref.update({
                'hive_participando': ArrayUnion([hive_id])
            })

            mensagem = f"{usuario_nome} começou a participar do seu hive '{titulo_hive}'."
            criar_notificacao(
                usuario_destino_id=dono_hive_id,
                tipo="participacao_hive",
                referencia_id=hive_id,
                mensagem=mensagem
            )
            Chat_Service.adicionar_ao_chat(hive_id,usuario_id)
            return {"mensagem": "Participação confirmada com sucesso!"}, 200

    except Exception as e:
        return {"erro": f"Erro ao participar do hive: {str(e)}"}, 500


# Implementado
@token_required
def cancelar_participacao(hive_id):
    usuario_id = g.user_id

    hive_ref = db.collection('Hive').document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()
    participantes = hive_data.get("participantes", [])

    if usuario_id not in participantes:
        return {
            "mensagem": "Você não está participando deste hive."
        }, 200

    if hive_data.get("usuario_id") == usuario_id:
        return {
            "mensagem": "O criador do hive não pode cancelar a própria participação.",
        }, 200

    try:
        hive_ref.update({
            'participantes': firestore.ArrayRemove([usuario_id])
        })

        user_ref = db.collection('Usuarios').document(usuario_id)
        user_ref.update({
            'hive_participando': firestore.ArrayRemove([hive_id])
        })
        Chat_Service.remover_do_chat(hive_id,[usuario_id])
        return {"mensagem": "Participação cancelada com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao cancelar participação: {str(e)}"}, 500


# Implementado
@token_required
def listarParticipandoHive():
    usuario_id = g.user_id  

    try:
        user_ref = db.collection('Usuarios').document(usuario_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return {"erro": "Usuário não encontrado."}, 404

        user_data = user_doc.to_dict()
        hive_ids = user_data.get('hive_participando', [])

        if not hive_ids:
            return jsonify({"mensagem": "Você não está participando de nenhum hive ou torneio."}), 200

        hive_ref = db.collection('Hive')
        hive = []
        for hive_id in hive_ids:
            hive_doc = hive_ref.document(hive_id).get()
            if hive_doc.exists:
                hive_data = hive_doc.to_dict()
                hive_data['id'] = hive_doc.id
                hive.append(hive_data)

        return jsonify(hive), 200

    except Exception as e:
        return {"erro": f"Erro ao listar hive participando: {str(e)}"}, 500
    

# Implementado
@token_required
def decidirParticipantesHive(hive_id, usuario_id, acao):
    usuario_dono = g.user_id
    hive_ref = db.collection("Hive").document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "Hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()

    if hive_data["usuario_id"] != usuario_dono:
        return {
            "mensagem": "Apenas o dono do hive pode aprovar ou recusar participantes."
        }, 200

    pendentes = hive_data.get("pendentes", [])
    if usuario_id not in pendentes:
        return {
            "mensagem": "Usuário não está na lista de pendentes.",
        }, 200

    try:
        titulo_hive = hive_data.get("titulo", "sem título")

        if acao == "aceitar":
            hive_ref.update({
                "pendentes": firestore.ArrayRemove([usuario_id]),
                "participantes": ArrayUnion([usuario_id])
            })

            db.collection("Usuarios").document(usuario_id).update({
                "hive_pendentes": firestore.ArrayRemove([hive_id]),
                "hive_participando": ArrayUnion([hive_id])
            })

            mensagem = f"Você foi aceito para participar do hive '{titulo_hive}'!"
            criar_notificacao(
                usuario_destino_id=usuario_id,
                tipo="hive_aceito",
                referencia_id=hive_id,
                mensagem=mensagem
            )   
            Chat_Service.adicionar_ao_chat(hive_id,usuario_id)

            return {"mensagem": "Usuário aceito no hive e notificado."}, 200

        elif acao == "recusar":
            hive_ref.update({
                "pendentes": firestore.ArrayRemove([usuario_id])
            })

            db.collection("Usuarios").document(usuario_id).update({
                "hive_pendentes": firestore.ArrayRemove([hive_id])
            })

            mensagem = f"Sua solicitação para participar do hive '{titulo_hive}' foi recusada."
            criar_notificacao(
                usuario_destino_id=usuario_id,
                tipo="hive_recusado",
                referencia_id=hive_id,
                mensagem=mensagem
            )

            return {"mensagem": "Usuário recusado e notificado."}, 200

        else:
            return {"erro": "Ação inválida"}, 400

    except Exception as e:
        return {"erro": f"Erro ao processar a decisão: {str(e)}"}, 500
    

# Implementado
@token_required
def listarPendentesHive(hive_id):
    usuario_dono = g.user_id
    hive_ref = db.collection("Hive").document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()

    if hive_data.get("usuario_id") != usuario_dono:
        return {"erro": "Apenas o dono do hive pode ver os pendentes."}, 200

    pendentes_ids = hive_data.get("pendentes", [])
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


# Implementado
@token_required
def cancelar_solicitacao(hive_id):
    usuario_id = g.user_id

    hive_ref = db.collection('Hive').document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "Hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()
    pendentes = hive_data.get("pendentes", [])

    if usuario_id not in pendentes:
        return {
            "mensagem": "Você não possui uma solicitação pendente para este hive."
        }, 200

    try:
        hive_ref.update({
            'pendentes': firestore.ArrayRemove([usuario_id])
        })

        user_ref = db.collection('Usuarios').document(usuario_id)
        user_ref.update({
            'hive_pendentes': firestore.ArrayRemove([hive_id])
        })


        return {"mensagem": "Solicitação de participação cancelada com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao cancelar solicitação: {str(e)}"}, 500
    
    
# Implementado
@token_required
def listar_participantes_hive(hive_id):
    usuario_dono = g.user_id
    hive_ref = db.collection("Hive").document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "Hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()

    if hive_data.get("usuario_id") != usuario_dono:
        return {"erro": "Apenas o dono do hive pode listar os participantes."}, 403

    participantes_ids = hive_data.get("participantes", [])
    participantes_info = []

    for user_id in participantes_ids:
        user_doc = db.collection("Usuarios").document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            participantes_info.append({
                "id": user_id,
                "nome_completo": user_data.get("nome_completo"),
                "username": user_data.get("username"),
                "foto_perfil": user_data.get("foto_perfil")
            })

    return {"participantes": participantes_info}, 200



@token_required
def remover_participante_hive(hive_id, usuario_remover_id):
    usuario_dono = g.user_id
    hive_ref = db.collection("Hive").document(hive_id)
    hive_doc = hive_ref.get()

    if not hive_doc.exists:
        return {"erro": "Hive não encontrado."}, 404

    hive_data = hive_doc.to_dict()
    participantes = hive_data.get("participantes", [])

    if hive_data.get("usuario_id") != usuario_dono:
        return {"erro": "Apenas o dono do hive pode remover participantes."}, 403

    if usuario_remover_id == usuario_dono:
        return {"erro": "O dono do hive não pode remover a si mesmo."}, 400

    if usuario_remover_id not in participantes:
        return {"erro": "O usuário especificado não está participando deste hive."}, 404

    try:
        hive_ref.update({
            'participantes': firestore.ArrayRemove([usuario_remover_id])
        })

        user_ref = db.collection('Usuarios').document(usuario_remover_id)
        user_ref.update({
            'hive_participando': firestore.ArrayRemove([hive_id])
        })

        Chat_Service.remover_do_chat(hive_id, usuario_remover_id)

        titulo_hive = hive_data.get("titulo", "sem título")
        mensagem = f"Você foi removido do hive '{titulo_hive}' pelo criador."
        criar_notificacao(
            usuario_destino_id=usuario_remover_id,
            tipo="remocao_hive",
            referencia_id=hive_id,
            mensagem=mensagem
        )

        return {"mensagem": f"Usuário removido do hive '{titulo_hive}' com sucesso."}, 200

    except Exception as e:
        return {"erro": f"Erro ao remover participante: {str(e)}"}, 500