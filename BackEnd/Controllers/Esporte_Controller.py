from flask import Blueprint, request, jsonify
from Services.Esporte_Service import adicionar_esporte, listar_esportes, atualizar_esporte_por_ID, excluir_esporte_por_ID

esporte_bp = Blueprint('esporte_bp', __name__, url_prefix="/esportes")


# Rota para adicionar um novo esporte
@esporte_bp.route('/AdicionarEsporte', methods=['POST'])
def adicionar():

    try:
        data = request.get_json()

    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400
    

    if not data:
        return jsonify({"erro": "Dados do evento não fornecidos"}), 400
    

    nome = data.get('nome')
    descricao = data.get('descricao')

    if not nome or not descricao:
        return jsonify({"erro": "Campos 'nome' e 'descricao' são obrigatórios"}), 400


    resposta, status = adicionar_esporte(nome, descricao)
    return jsonify(resposta), status



# Rota para listar todos os esportes
@esporte_bp.route('/ListarEsportes', methods=['GET'])
def listar():
    try:
        esportes = listar_esportes()
        return jsonify(esportes), 200    
    except Exception as e:
        print(f"Erro na rota listar_eventos_route: {e}")
        return jsonify({"erro": "Erro interno ao listar eventos"}), 500




# Rota para atualizar um esporte
@esporte_bp.route('/AtualizarEsporte/<esporte_id>', methods=['PUT'])
def atualizar(esporte_id):
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    nome = data.get('nome')
    descricao = data.get('descricao')

    if not nome and not descricao:
        return jsonify({"erro": "Informe ao menos 'nome' ou 'descricao' para atualizar"}), 400

    resposta, status = atualizar_esporte_por_ID(esporte_id, nome, descricao)
    return jsonify(resposta), status



# Rota para excluir um esporte
@esporte_bp.route('/ExcluirEsporte/<esporte_id>', methods=['DELETE'])
def excluir(esporte_id):
    resposta, status = excluir_esporte_por_ID(esporte_id)
    return jsonify(resposta), status
