from flask import Blueprint, Flask, request, jsonify
from Services import Treino_Service


treino_bp = Blueprint('treino_bp', __name__, url_prefix="/treino" )

# Implementado
@treino_bp.route('/AdicionarTreino', methods=['POST'])
def criar_treino():
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    nome_esporte = request.form.get("nome_esporte")
    data_hora_str = request.form.get("data_hora_str")
    lugar = request.form.get("lugar")
    tempo_treinado = request.form.get("tempo_treinado")

    if not all([titulo, descricao, nome_esporte, data_hora_str, lugar, tempo_treinado]):
        return {"erro": "Todos os campos obrigatórios devem ser preenchidos."}, 400

    try:
        tempo_treinado = float(tempo_treinado)
    except ValueError:
        return {"erro": "O tempo treinado deve ser um número."}, 400

    arquivo_imagem = request.files.get("arquivo_imagem")

    treino_dict, status = Treino_Service.adicionar_treino(
        titulo=titulo,
        descricao=descricao,
        nome_esporte=nome_esporte,
        data_hora_str=data_hora_str,
        lugar=lugar,
        tempo_treinado=tempo_treinado,
        arquivo_imagem=arquivo_imagem
    )

    return treino_dict, status



# Implementado
@treino_bp.route('/ListarTreino', methods=['GET'])
def listar_treino():
    treino_list, status = Treino_Service.listar_treino_por_userID()
    return treino_list, status



# Implementado
@treino_bp.route('/ExcluirTreino', methods=['DELETE'])
def excluir_treino():
    data = request.get_json()

    treino_id = data.get('treino_id')

    if not treino_id:
        return jsonify({"erro": "O campo 'treino_id' é obrigatório."}), 400

    response, status = Treino_Service.excluir_treino_por_treinoID(treino_id)
    return response, status



# Implementado
@treino_bp.route('/AtualizarTreino', methods=['PUT'])
def atualizar_treino():
    treino_id = request.form.get('treino_id')
    if not treino_id:
        return jsonify({"erro": "O campo 'treino_id' é obrigatório."}), 400

    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    nome_esporte = request.form.get('nome_esporte')
    data_hora_str = request.form.get('data_hora_str')
    lugar = request.form.get('lugar')
    tempo_treinado = request.form.get('tempo_treinado')

    arquivo_imagem = request.files.get('arquivo_imagem')  
    print(arquivo_imagem)

    response, status = Treino_Service.atualizar_treino_por_treinoID(
        treino_id=treino_id,
        titulo=titulo,
        descricao=descricao,
        nome_esporte=nome_esporte,
        data_hora_str=data_hora_str,
        lugar=lugar,
        tempo_treinado=tempo_treinado,
        arquivo_imagem=arquivo_imagem
    )

    return jsonify(response), status



# Implementado
@treino_bp.route('/ListarTreinoPorID', methods=['GET'])
def listar_treino_por_id():
    treino_id = request.args.get('treino_id')

    if not treino_id:
        return jsonify({"erro": "O campo 'treino_id' é obrigatório."}), 400

    response, status = Treino_Service.listar_treino_por_treinoID(treino_id)
    return jsonify(response), status