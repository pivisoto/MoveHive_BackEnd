from flask import Blueprint, jsonify, g, request
from firebase_admin import firestore
from middlewares.auth_token import token_required
from Services import Notificacao_Service


notificacao_bp = Blueprint('notificacao_bp', __name__, url_prefix='/notificacao')
db = firestore.client()


# Implementado
@notificacao_bp.route('/MinhaNotificacoes', methods=['GET'])
def pegar_minhas_notificacoes():
    resposta, status_code = Notificacao_Service.pegar_notificacoes()
    return jsonify(resposta), status_code

# Implementado
@notificacao_bp.route("/NotificacaoLida", methods=["PUT"])
def marcar_como_lida():
    try:
        dados = request.get_json()
        notificacao_id = dados.get("notificacao_id")

        if not notificacao_id:
            return jsonify({"erro": "O campo 'notificacao_id' é obrigatório"}), 400

        resposta, status_code = Notificacao_Service.marcar_notificacao_lida(notificacao_id)
        return jsonify(resposta), status_code

    except Exception as e:
        return jsonify({"erro": f"Erro ao marcar notificação como lida: {str(e)}"}), 500
    

# Implementado
@notificacao_bp.route("/DeletarNotificacao", methods=["DELETE"])
def deletar():
    try:
        dados = request.get_json()
        notificacao_id = dados.get("notificacao_id")

        resposta = Notificacao_Service.deletar_notificacao(notificacao_id)

        if "erro" in resposta:
            return jsonify(resposta), 404
        return jsonify(resposta), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao processar requisição: {str(e)}"}), 500