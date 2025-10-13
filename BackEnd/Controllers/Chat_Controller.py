from flask import Blueprint, request, jsonify
from Services import Chat_Service

chat_bp = Blueprint('chat_bp', __name__, url_prefix="/chat")

# Rota para Criar Chat
@chat_bp.route('/CriarChat', methods=['POST'])
def criarChat():
    try:
        data = request.get_json()
        nome_chat = data.get('nome_chat')
        lista_participantes = data.get('participantes')
        foto_chat = request.files.get("arquivo_foto")
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400
    
    if foto_chat:
        pass
    else:
        foto_chat = ''

    if not data:
        return jsonify({"erro": "Dados do chat não fornecidos"}), 400

    if not nome_chat:
        return jsonify({"erro": "Nome do chat é obrigatório"}), 400
    id_evento=''
    return Chat_Service.criar_chat(nome_chat,lista_participantes,id_evento,foto_chat)

# Rota para Remover Participante
@chat_bp.route('/AdicionarParticipantes', methods=['POST'])
def AdicionarParticipantes():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        novos_participantes = data.get('participantes_novos')
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do chat não fornecidos"}), 400

    if not chat_id or not novos_participantes:
        return jsonify({"erro": "chat_id e participantes_novos são obrigatórios"}), 400
    
    return Chat_Service.adicionar_ao_chat(chat_id,novos_participantes)

# Rota para Remover Participante
@chat_bp.route('/RemoverParticipantes', methods=['POST'])
def RemoveParticipantes():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        usuario_id_remover = data.get('usuarios_remover')
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do chat não fornecidos"}), 400

    if not chat_id or not usuario_id_remover:
        return jsonify({"erro": "chat_id e usuarios_remover são obrigatórios"}), 400
    
    return Chat_Service.remover_do_chat(chat_id,usuario_id_remover)

# Rota para Remover Participante
@chat_bp.route('/MudarNome', methods=['POST'])
def MudarNomeChat():
    try:
        data = request.get_json()
        chat_id = data.get('chat_id')
        nome_novo = data.get('nome_novo')
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do chat não fornecidos"}), 400

    if not chat_id:
        return jsonify({"erro": "chat_id e nome_novo obrigatórios"}), 400
    
    return Chat_Service.mudar_nome_chat(chat_id,nome_novo)

# Rota para Enviar Mensagem
@chat_bp.route('/MandarMensagem', methods=['POST'])
def EnviarMensagemChat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Dados não fornecidos."}), 400
        
        chat_id = data.get('chat_id')
        texto_mensagem = data.get('texto_mensagem')
        
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not chat_id or not texto_mensagem:
        return jsonify({"erro": "Os campos 'chat_id' e 'texto_mensagem' são obrigatórios."}), 400
    
    return Chat_Service.mandar_mensagem(chat_id, texto_mensagem)

# Rota para apagar o chat
@chat_bp.route('/ApagarChat', methods=['POST'])
def ApagarChat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"erro": "Dados não fornecidos."}), 400
        
        chat_id = data.get('chat_id')
        
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not chat_id:
        return jsonify({"erro": "Os campos 'chat_id' é obrigatório."}), 400

    return Chat_Service.apagar_chat()



# Rota para Exibir os chats 
@chat_bp.route('/ExibirChats', methods=['GET'])
def ExibirChats():
    return Chat_Service.exibir_chats()

# Rota para Exibir as conversas
@chat_bp.route('/ExibirConversa/<string:chat_id>', methods=['GET'])
def ExibirConversas(chat_id):
    try:
        if not chat_id:
             return jsonify({"erro": "O campo 'chat_id' é obrigatório."}), 400
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400
    
    return Chat_Service.exibir_conversa(chat_id)

