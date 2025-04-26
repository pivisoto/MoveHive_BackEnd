from flask import Blueprint, request, jsonify
from Services.Esporte_Service import adicionar_esporte, listar_esportes, atualizar_esporte, excluir_esporte

esporte_bp = Blueprint('esporte_bp', __name__)


# Rota para adicionar um novo esporte
@esporte_bp.route('/esportes', methods=['POST'])
def adicionar():
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')

    if not nome or not descricao:
        return jsonify({"erro": "Campos 'nome' e 'descricao' são obrigatórios"}), 400

    resposta, status = adicionar_esporte(nome, descricao)
    return jsonify(resposta), status



# Rota para listar todos os esportes
@esporte_bp.route('/esportes', methods=['GET'])
def listar():
    esportes = listar_esportes()
    return jsonify(esportes), 200




# Rota para atualizar um esporte
@esporte_bp.route('/esportes/<id>', methods=['PUT'])
def atualizar(id):
    data = request.get_json()
    nome = data.get('nome')
    descricao = data.get('descricao')

    if not nome and not descricao:
        return jsonify({"erro": "Informe ao menos 'nome' ou 'descricao' para atualizar"}), 400

    resposta, status = atualizar_esporte(id, nome, descricao)
    return jsonify(resposta), status




# Rota para excluir um esporte
@esporte_bp.route('/esportes/<id>', methods=['DELETE'])
def excluir(id):
    resposta, status = excluir_esporte(id)
    return jsonify(resposta), status
