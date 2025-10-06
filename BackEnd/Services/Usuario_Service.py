from datetime import date, datetime,  timedelta, timezone
from email import utils
import time
import os
import random
import string
import uuid
import bcrypt
from firebase_admin import firestore, credentials, storage
from flask import g, jsonify
from Models.Usuario_Model import Usuario
from middlewares.generate_token import generate_token
from middlewares.auth_token import token_required
import firebase_admin
import logging
from firebase_admin import firestore
import smtplib
from email.mime.text import MIMEText
from utils import enviar_email
import json
from Services.Notificacao_Service import criar_notificacao




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
bucket = storage.bucket()
db = firestore.client()


# Implementado
def calcular_idade(data_nascimento):
    hoje = date.today()
    idade = hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
    return idade



# Função para Registar Usuario
# Implementado
def registrar_usuario(nome_completo, username, data_nascimento_str, email, senha):
    usuarios_ref = db.collection('Usuarios')

    if list(usuarios_ref.where('email', '==', email).limit(1).stream()):
        return {"erro": "E-mail já cadastrado"}
    
    if list(usuarios_ref.where('username', '==', username).limit(1).stream()):
        return {"erro": "Username já cadastrado"}

    try:
        data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
    except ValueError:
        return {"erro": "Data de nascimento inválida. Use o formato YYYY-MM-DD."}

    if data_nascimento > date.today():
        return {"erro": "Data de nascimento não pode ser futura."}

    if data_nascimento.year < 1900:
        return {"erro": "Ano de nascimento inválido."}

    idade = calcular_idade(data_nascimento)
    if idade < 18:
        return {"erro": "É necessário ter pelo menos 18 anos para se cadastrar."}

    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    usuario = Usuario(
        nome_completo=nome_completo,
        username=username,
        email=email,
        senha=senha_hash,
        data_nascimento=data_nascimento_str
    )

    doc_ref = usuarios_ref.document(usuario.id)
    doc_ref.set(usuario.to_dict())

    bucket = storage.bucket()
    blob = bucket.blob(f'Usuarios/{usuario.id}/Fotos/.init')
    blob.upload_from_string('Pasta Fotos inicializada', content_type='text/plain')

    token = generate_token(doc_ref.id)

    return {"token": token}, 201



# Função para Logar Usuarios
def login_usuarios(email, senha):
    usuario_doc = db.collection('Usuarios').where('email', '==', email).limit(1).stream()
    usuario_doc = next(usuario_doc, None)
    tipo_usuario = "usuario"

    if not usuario_doc:
        usuario_doc = db.collection('UsuariosEmpresa').where('email', '==', email).limit(1).stream()
        usuario_doc = next(usuario_doc, None)
        tipo_usuario = "empresa"

    if not usuario_doc:
        return {"erro": "E-mail não encontrado"}, 404

    dados = usuario_doc.to_dict()

    if not bcrypt.checkpw(senha.encode('utf-8'), dados['senha'].encode('utf-8')):
        return {"erro": "Senha incorreta"}, 401

    token = generate_token(usuario_doc.id, tipo_usuario=tipo_usuario)

    return {"token": token, "tipo_usuario": tipo_usuario}, 200


# Implementado
@token_required
def adicionar_dados_modal(dados_modal, arquivo_foto=None):
    usuario_id = g.user_id
    doc_ref = db.collection('Usuarios').document(usuario_id)

    if not doc_ref.get().exists:
        return {"erro": "Usuário não encontrado"}, 404

    dados_para_adicionar = {}

    if arquivo_foto:
        caminho = f"Usuarios/{usuario_id}/Fotos/foto_perfil.jpg"
        blob = bucket.blob(caminho)
        blob.upload_from_file(arquivo_foto, content_type=arquivo_foto.content_type)
        blob.make_public() 

        dados_para_adicionar['foto_perfil'] = blob.public_url

    campos = ['biografia', 'cidade', 'estado', 'esportes_praticados']
    for campo in campos:
        if campo in dados_modal:
            dados_para_adicionar[campo] = dados_modal[campo]

    doc_ref.update(dados_para_adicionar)

    return {"status": "sucesso", "mensagem": "Informações atualizadas com sucesso"}, 200


# Implementado
@token_required
def editar_usuario(dados, foto_perfil=None):
    usuario_id = g.user_id
    usuario_ref = db.collection('Usuarios').document(usuario_id)

    try:
        usuario_doc = usuario_ref.get()
        if not usuario_doc.exists:
            return {"erro": "Usuário não encontrado."}, 404
    except Exception as e:
        return {"erro": f"Erro ao acessar o banco de dados: {str(e)}"}, 500

    updates = {}
    
    for campo, valor in dados.items():
        if valor is None or valor == '':
            continue 

        try:
            if campo == 'username':
                usuarios_com_mesmo_username = db.collection('Usuarios').where('username', '==', valor).limit(1).get()
                if len(usuarios_com_mesmo_username) > 0 and usuarios_com_mesmo_username[0].id != usuario_id:
                    return {"erro": f"O username '{valor}' já está em uso."}, 409 
                updates[campo] = valor

            elif campo == 'email':
                usuarios_com_mesmo_email = db.collection('Usuarios').where('email', '==', valor).limit(1).get()
                if len(usuarios_com_mesmo_email) > 0 and usuarios_com_mesmo_email[0].id != usuario_id:
                    return {"erro": f"O email '{valor}' já está em uso."}, 409
                updates[campo] = valor

            elif campo == 'senha':
               senha_hash = bcrypt.hashpw(valor.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
               updates[campo] = senha_hash
               
            elif campo == 'data_nascimento':
                dt_nascimento = datetime.strptime(valor, "%Y-%m-%d")
                hoje = datetime.now()
                
                if dt_nascimento.year < 1900:
                    return {"erro": "O ano de nascimento não pode ser anterior a 1900."}, 400
                if dt_nascimento > hoje:
                    return {"erro": "A data de nascimento não pode ser no futuro."}, 400
                
                idade = hoje.year - dt_nascimento.year - ((hoje.month, hoje.day) < (dt_nascimento.month, dt_nascimento.day))
                if idade < 18:
                    return {"erro": "O usuário deve ter pelo menos 18 anos."}, 400
                
                updates[campo] = valor
            
            elif campo == 'esportes_praticados':
                try:
                    esportes_obj = json.loads(valor)
                    if not isinstance(esportes_obj, dict):
                        return {"erro": "O formato para esportes_praticados deve ser um objeto JSON válido."}, 400
                    
                    updates[campo] = esportes_obj

                except json.JSONDecodeError:
                    return {"erro": "Formato inválido para o campo 'esportes_praticados'. Esperava-se um JSON."}, 400
            
            elif campo in ['nome_completo', 'biografia', 'estado', 'cidade']:
                updates[campo] = str(valor)

        except ValueError as e:
            return {"erro": f"Formato inválido para o campo '{campo}'. Detalhes: {e}"}, 400
        except Exception as e:
            return {"erro": f"Ocorreu um erro inesperado ao processar o campo '{campo}': {str(e)}"}, 500

    if foto_perfil:
        try:
            caminho = f"Usuarios/{usuario_id}/Fotos/foto_perfil.jpg"
            blob = bucket.blob(caminho)
            
            foto_perfil.seek(0)
            
            blob.upload_from_file(foto_perfil, content_type=foto_perfil.content_type)
            blob.make_public()
            
            timestamp = int(time.time())
            updates['foto_perfil'] = f"{blob.public_url}?v={timestamp}"
            
        except Exception as e:
            return {"erro": f"Erro ao fazer upload da imagem: {str(e)}"}, 500

    if not updates:
        return {"mensagem": "Nenhuma alteração foi feita."}, 200

    try:
        usuario_ref.update(updates)
        return {"mensagem": "Usuário atualizado com sucesso."}, 200
    except Exception as e:
        return {"erro": f"Erro ao atualizar o usuário no banco de dados: {str(e)}"}, 500

# Implementado
@token_required
def excluir_meu_usuario():
    try:
        usuario_id = g.user_id
        batch = db.batch()
        
        user_ref = db.collection('Usuarios').document(usuario_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            return {"erro": "Usuário não encontrado para exclusão."}, 404
        user_data = user_doc.to_dict()

        

        # Remover este usuário da lista de 'seguidores' de quem ele seguia
        if user_data.get('seguindo'):
            for followed_id in user_data['seguindo']:
                followed_ref = db.collection('Usuarios').document(followed_id)
                batch.update(followed_ref, {'seguidores': firestore.ArrayRemove([usuario_id])})

        # Remover este usuário da lista de 'seguindo' de seus seguidores
        if user_data.get('seguidores'):
            for follower_id in user_data['seguidores']:
                follower_ref = db.collection('Usuarios').document(follower_id)
                batch.update(follower_ref, {'seguindo': firestore.ArrayRemove([usuario_id])})
        
        # Remover o usuário de todos os eventos que ele estava participando
        events_participating_query = db.collection('Eventos').where('participantes', 'array_contains', usuario_id).stream()
        for evento in events_participating_query:
            batch.update(evento.reference, {'participantes': firestore.ArrayRemove([usuario_id])})


        # Excluir posts
        posts_query = db.collection('Postagens').where('usuario_id', '==', usuario_id).stream()
        for post in posts_query:
            batch.delete(post.reference)

        # Excluir eventos
        events_query = db.collection('Eventos').where('usuario_id', '==', usuario_id).stream()
        for evento in events_query:
            batch.delete(evento.reference)

        # Excluir treinos
        treinos_query = db.collection('Treinos').where('usuario_id', '==', usuario_id).stream()
        for treino in treinos_query:
            batch.delete(treino.reference)

        batch.delete(user_ref)

        batch.commit()

 
        prefix = f"Usuarios/{usuario_id}/"
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            blob.delete()

        return {"mensagem": "Usuário e todos os dados associados foram excluídos com sucesso."}, 200

    except Exception as e:
        print(f"Erro ao excluir usuário {usuario_id}: {str(e)}") 
        return {"erro": f"Ocorreu um erro interno ao tentar excluir o usuário: {str(e)}"}, 500

# Implementado
@token_required 
def meuPerfil():
    try:
            usuario_id = g.user_id

            usuario_ref = db.collection('Usuarios').document(usuario_id)
            usuario_doc = usuario_ref.get()

            if not usuario_doc.exists:

                return jsonify({'erro': 'Usuário não encontrado!'}), 404

            usuario_data = usuario_doc.to_dict()

            posts_query = db.collection('Posts').where('usuario_id', '==', usuario_id).stream()
            total_posts = len(list(posts_query))


            total_seguidores = len(usuario_data.get('seguidores', []))

           
            total_seguindo = len(usuario_data.get('seguindo', []))
           

            usuario_data['total_posts'] = total_posts
            usuario_data['seguidores_count'] = total_seguidores 
            usuario_data['seguindo_count'] = total_seguindo     

            usuario_data.pop('seguidores', None)
            usuario_data.pop('seguindo', None)
            
            usuario_data.pop('senha', None)

            return jsonify(usuario_data), 200

    except Exception as e:
            print(f"Erro ao buscar perfil do usuário {g.user_id}: {e}")
            return jsonify({'erro': f'Ocorreu um erro interno ao processar seu perfil.'}), 500

# Implementado
@token_required 
def verPerfil(usuario_id):
    try:
        usuario_ref = db.collection('Usuarios').document(usuario_id)
        usuario_doc = usuario_ref.get()

        if not usuario_doc.exists:
            return jsonify({'erro': 'Usuário não encontrado!'}), 404

        usuario_data = usuario_doc.to_dict()

        posts_query = db.collection('Posts').where('usuario_id', '==', usuario_id).stream()
        total_posts = len(list(posts_query))

        total_seguidores = len(usuario_data.get('seguidores', []))

        total_seguindo = len(usuario_data.get('seguindo', []))
       
        usuario_data['total_posts'] = total_posts
        usuario_data['seguidores_count'] = total_seguidores 
        usuario_data['seguindo_count'] = total_seguindo     

        usuario_data.pop('seguidores', None)
        usuario_data.pop('seguindo', None)
        usuario_data.pop('senha', None) 

        return jsonify(usuario_data), 200

    except Exception as e:
        print(f"Erro ao buscar perfil do usuário {usuario_id}: {e}")
        return jsonify({'erro': f'Ocorreu um erro interno ao processar o perfil.'}), 500

# Implementado
@token_required
def seguir_usuario(seguido_id):
    try:
        usuario_id = g.user_id

        if seguido_id == usuario_id:
            return {'erro': 'Você não pode seguir a si mesmo'}, 400

        usuario_ref = db.collection('Usuarios').document(usuario_id)
        seguido_ref = db.collection('Usuarios').document(seguido_id)

        usuario_doc = usuario_ref.get()
        seguido_doc = seguido_ref.get()

        if not usuario_ref.get().exists or not seguido_ref.get().exists:
            return {'erro': 'Usuário(s) não encontrado(s)'}, 404

        usuario_ref.update({
            'seguindo': firestore.ArrayUnion([seguido_id])
        })

        seguido_ref.update({
            'seguidores': firestore.ArrayUnion([usuario_id])
        })

        usuario_nome = usuario_doc.to_dict().get('username', 'Alguém')

        criar_notificacao(
            usuario_destino_id=seguido_id,
            tipo="seguindo",
            referencia_id=usuario_id,
            mensagem= f"{usuario_nome} começou a te seguir."
        )

        return {'mensagem': 'Usuário seguido com sucesso!'}, 200

    except Exception as e:
        return {'erro': str(e)}, 500
    
# Implementado
@token_required
def deixar_de_seguir_usuario(seguido_id):
    try:
        usuario_id = g.user_id

        if seguido_id == usuario_id:
            return {'erro': 'Você não pode deixar de seguir a si mesmo'}, 400

        usuario_ref = db.collection('Usuarios').document(usuario_id)
        seguido_ref = db.collection('Usuarios').document(seguido_id)

        if not usuario_ref.get().exists or not seguido_ref.get().exists:
            return {'erro': 'Usuário(s) não encontrado(s)'}, 404

        usuario_ref.update({
            'seguindo': firestore.ArrayRemove([seguido_id])
        })

        seguido_ref.update({
            'seguidores': firestore.ArrayRemove([usuario_id])
        })

        return {'mensagem': 'Usuário deixado de seguir com sucesso!'}, 200

    except Exception as e:
        return {'erro': str(e)}, 500

# Implementado
@token_required
def listar_usuarios_sem_filtro():
    try:
        usuario_logado_id = g.user_id

        usuario_logado_ref = db.collection('Usuarios').document(usuario_logado_id)
        usuario_logado_doc = usuario_logado_ref.get()

        if not usuario_logado_doc.exists:
            return {'erro': 'Usuário autenticado não encontrado'}, 404

        lista_seguindo = usuario_logado_doc.to_dict().get('seguindo', [])

        todos_os_usuarios_ref = db.collection('Usuarios').stream()

        usuarios_sugeridos = []
        for doc in todos_os_usuarios_ref:
            
            if doc.id == usuario_logado_id:
                continue  # não incluir eu mesmo
            
            if doc.id in lista_seguindo:
                continue  # não incluir quem já sigo

            dados = doc.to_dict()

            usuarios_sugeridos.append({
                'id': doc.id, 
                'username': dados.get('username'),
                'nome_completo': dados.get('nome_completo'),
                'foto_perfil': dados.get('foto_perfil'),
                'biografia': dados.get('biografia', ''),
                'cidade': dados.get('cidade', ''),
                'estado': dados.get('estado', ''),
                'esportes_praticados': dados.get('esportes_praticados', {})
            })

        return {'usuarios': usuarios_sugeridos}, 200

    except Exception as e:
        print(f"Erro em listar_usuarios: {e}") 
        return {'erro': str(e)}, 500
        
# Implementado
@token_required
def listar_usuarios_com_filtro():
    try:
        usuario_logado_id = g.user_id
        usuario_logado_doc = db.collection('Usuarios').document(usuario_logado_id).get()

        if not usuario_logado_doc.exists:
            return {'erro': 'Usuário autenticado não encontrado'}, 404

        usuario_logado = usuario_logado_doc.to_dict()
        lista_seguindo = set(usuario_logado.get('seguindo', []))
        meus_esportes = set(usuario_logado.get('esportes_praticados', {}))
        minha_cidade = usuario_logado.get('cidade', '')
        meu_estado = usuario_logado.get('estado', '')

        def buscar_usuarios(criterio_relaxado=False):
            usuarios = []
            for doc in db.collection('Usuarios').stream():
                if doc.id == usuario_logado_id:
                    continue
                if doc.id in lista_seguindo:
                    continue

                dados = doc.to_dict()
                esportes_usuario = set(dados.get('esportes_praticados', {}))
                mesma_cidade = dados.get('cidade') == minha_cidade and minha_cidade != ''
                mesmo_estado = dados.get('estado') == meu_estado and meu_estado != ''

                if not criterio_relaxado:
                    if not (mesma_cidade or mesmo_estado or len(meus_esportes.intersection(esportes_usuario)) > 0):
                        continue

                usuarios.append({
                    'id': doc.id,
                    'username': dados.get('username'),
                    'nome_completo': dados.get('nome_completo'),
                    'foto_perfil': dados.get('foto_perfil'),
                    'biografia': dados.get('biografia', ''),
                    'cidade': dados.get('cidade', ''),
                    'estado': dados.get('estado', ''),
                    'esportes_praticados': dados.get('esportes_praticados', {})
                })
            return usuarios

        usuarios_sugeridos = buscar_usuarios()

        if not usuarios_sugeridos:
            usuarios_sugeridos = buscar_usuarios(criterio_relaxado=True)

        if not usuarios_sugeridos:
            todos = list(db.collection('Usuarios').stream())
            usuarios_sugeridos = [{
                'id': doc.id,
                'username': doc.to_dict().get('username'),
                'nome_completo': doc.to_dict().get('nome_completo'),
                'foto_perfil': doc.to_dict().get('foto_perfil'),
                'biografia': doc.to_dict().get('biografia', ''),
                'cidade': doc.to_dict().get('cidade', ''),
                'estado': doc.to_dict().get('estado', ''),
                'esportes_praticados': doc.to_dict().get('esportes_praticados', {})
            } for doc in todos if doc.id != usuario_logado_id and doc.id not in lista_seguindo]

        return {'usuarios': usuarios_sugeridos}, 200

    except Exception as e:
        print(f"Erro em listar_usuarios_com_filtro: {e}")
        return {'erro': str(e)}, 500

# Implementado
@token_required
def listar_usuarios_seguindo():
    try:
        usuario_logado_id = g.user_id
        usuario_logado_ref = db.collection('Usuarios').document(usuario_logado_id)
        usuario_logado_doc = usuario_logado_ref.get()

        if not usuario_logado_doc.exists:
            return {'erro': 'Usuário autenticado não encontrado'}, 404

        lista_seguindo = usuario_logado_doc.to_dict().get('seguindo', [])

        usuarios_seguindo = []
        for user_id in lista_seguindo:
            user_doc = db.collection('Usuarios').document(user_id).get()
            if not user_doc.exists:
                continue  # pula caso o usuário não exista mais

            dados = user_doc.to_dict()
            usuarios_seguindo.append({
                'id': user_id,
                'username': dados.get('username'),
                'nome_completo': dados.get('nome_completo'),
                'foto_perfil': dados.get('foto_perfil'),
                'biografia': dados.get('biografia', ''),
                'cidade': dados.get('cidade', ''),
                'estado': dados.get('estado', ''),
                'esportes_praticados': dados.get('esportes_praticados', {})
            })

        return {'usuarios_seguindo': usuarios_seguindo}, 200

    except Exception as e:
        print(f"Erro em listar_usuarios_seguindo: {e}")
        return {'erro': str(e)}, 500
    
# Implementado
@token_required
def listar_seguidores():
    try:
        usuario_logado_id = g.user_id
        usuario_logado_ref = db.collection('Usuarios').document(usuario_logado_id)
        usuario_logado_doc = usuario_logado_ref.get()

        if not usuario_logado_doc.exists:
            return {'erro': 'Usuário autenticado não encontrado'}, 404

        # Busca todos os usuários que seguem o usuário logado
        query = db.collection('Usuarios').where('seguindo', 'array_contains', usuario_logado_id).stream()

        seguidores = []
        for user_doc in query:
            dados = user_doc.to_dict()
            seguidores.append({
                'id': user_doc.id,
                'username': dados.get('username'),
                'nome_completo': dados.get('nome_completo'),
                'foto_perfil': dados.get('foto_perfil'),
                'biografia': dados.get('biografia', ''),
                'cidade': dados.get('cidade', ''),
                'estado': dados.get('estado', ''),
                'esportes_praticados': dados.get('esportes_praticados', {})
            })

        return {'seguidores': seguidores}, 200

    except Exception as e:
        print(f"Erro em listar_seguidores: {e}")
        return {'erro': str(e)}, 500

# Implementado
@token_required
def competicao_usuarios_todos():
    try:
        # Filtra apenas usuários com pontos > 0
        usuarios_ref = (
            db.collection('Usuarios')
            .where('pontos', '>', 0)
            .order_by('pontos', direction=firestore.Query.DESCENDING)
            .stream()
        )

        usuarios = []
        for doc in usuarios_ref:
            dados = doc.to_dict()

            usuario_filtrado = {
                'nome_completo': dados.get('nome_completo'),
                'username': dados.get('username'),
                'pontos': dados.get('pontos'),
                'foto_perfil': dados.get('foto_perfil')
            }
            usuarios.append(usuario_filtrado)

        return jsonify(usuarios), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500
      
# Implementado
@token_required
def competicao_usuarios_seguindo():
    try:
        
        usuario_atual_id = g.user_id

        usuario_doc_ref = db.collection('Usuarios').document(usuario_atual_id)
        usuario_doc = usuario_doc_ref.get()

        if not usuario_doc.exists:
            return jsonify({'erro': 'Usuário autenticado não encontrado no banco de dados'}), 404
            
        dados_usuario_atual = usuario_doc.to_dict()


        ids_seguindo = dados_usuario_atual.get('seguindo', [])


        ids_para_buscar = set(ids_seguindo)
        ids_para_buscar.add(usuario_atual_id)

        usuarios = []
        for user_id in ids_para_buscar:
            doc_ref = db.collection('Usuarios').document(user_id).get()
            if doc_ref.exists:
                dados = doc_ref.to_dict()
                
                usuario_filtrado = {
                    'nome_completo': dados.get('nome_completo'),
                    'username': dados.get('username'),
                    'pontos': dados.get('pontos', 0), 
                    'foto_perfil': dados.get('foto_perfil')
                }
                usuarios.append(usuario_filtrado)

        usuarios_ordenados = sorted(usuarios, key=lambda u: u['pontos'], reverse=True)

        return jsonify(usuarios_ordenados), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# Implementado
def solicitar_reset_senha(email):
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('email', '==', email).limit(1).get()

    msg_retorno = {"msg": "Se o e-mail estiver em nossa base, você receberá um código para redefinir sua senha."}

    if not query:
        logger.info(f"Solicitação de reset para e-mail não cadastrado: {email}")
        return msg_retorno, 404

    try:
        usuario_doc = query[0]
        usuario_id = usuario_doc.id

        codigo = ''.join(random.choices(string.digits, k=6))
        
        codigo_hash = bcrypt.hashpw(codigo.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        exp = datetime.now(timezone.utc) + timedelta(minutes=10)  

        usuarios_ref.document(usuario_id).update({
            "reset_code_hash": codigo_hash,
            "reset_code_exp": exp
        })

        enviar_email.enviar_email_reset(destinatario=email, codigo=codigo)

        
        logger.info(f"E-mail de reset enviado com sucesso para {email}.")

    except Exception as e:
        logger.error(f"Falha ao processar a solicitação de reset para {email}. Erro: {e}")
        if 'usuario_id' in locals():
            usuarios_ref.document(usuario_id).update({
                "reset_code_hash": firestore.DELETE_FIELD,
                "reset_code_exp": firestore.DELETE_FIELD
            })
        return msg_retorno, 500
            
    return msg_retorno, 200


# Implementado
def verificar_codigo_reset(email, codigo):
    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('email', '==', email).limit(1).get()

    if not query:
        return {"valido": False, "msg": "Código inválido ou expirado."}

    usuario_doc = query[0].to_dict()

    if "reset_code_hash" not in usuario_doc or "reset_code_exp" not in usuario_doc:
        return {"valido": False, "msg": "Código inválido ou expirado."}
        
    if datetime.now(timezone.utc) > usuario_doc["reset_code_exp"]:
        return {"valido": False, "msg": "Código expirado. Solicite um novo."}

    codigo_valido = bcrypt.checkpw(codigo.encode('utf-8'), usuario_doc["reset_code_hash"].encode('utf-8'))

    if not codigo_valido:
        return {"valido": False, "msg": "Código inválido ou expirado."}

    return {"valido": True, "msg": "Código verificado com sucesso."}


# Implementado
def redefinir_senha(email, codigo, nova_senha):
    verificacao = verificar_codigo_reset(email, codigo)
    if not verificacao["valido"]:
        return {"sucesso": False, "msg": verificacao["msg"]}

    usuarios_ref = db.collection('Usuarios')
    query = usuarios_ref.where('email', '==', email).limit(1).get()
    
    if not query:
         return {"sucesso": False, "msg": "Usuário não encontrado."}

    try:
        usuario_id = query[0].id
        
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        usuarios_ref.document(usuario_id).update({
            "senha": nova_senha_hash,
            "reset_code_hash": firestore.DELETE_FIELD,
            "reset_code_exp": firestore.DELETE_FIELD
        })
        
        logger.info(f"Senha para o e-mail {email} alterada com sucesso.")
        return {"sucesso": True, "msg": "Sua senha foi alterada com sucesso!"}

    except Exception as e:
        logger.error(f"Erro ao redefinir a senha para {email}. Erro: {e}")
        return {"sucesso": False, "msg": "Ocorreu um erro ao tentar alterar sua senha. Tente novamente."}
