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
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do chat não fornecidos"}), 400

    if not nome_chat:
        return jsonify({"erro": "Nome do chat é obrigatório"}), 400
    
    return Chat_Service.criar_chat(nome_chat,lista_participantes)

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