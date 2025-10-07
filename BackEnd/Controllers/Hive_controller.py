from flask import Blueprint, jsonify, request
from Services import Hive_Service

hive_bp = Blueprint('hive_bp', __name__, url_prefix="/hive")

# Implementado
@hive_bp.route('/AdicionarHive', methods=['POST'])
def criar_hive():
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    esporte_nome = request.form.get("esporte_nome")
    data_hora_str = request.form.get("data_hora_str")
    localizacao = request.form.get("localizacao")
    endereco = request.form.get("endereco")
    max_participantes = request.form.get("max_participantes")
    privado = request.form.get("privado", "false").lower() == "true"
    observacoes = request.form.get("observacoes", "")

    
    if not all([titulo, descricao, esporte_nome, data_hora_str, localizacao, endereco, max_participantes]):
        return {"erro": "Todos os campos obrigatórios devem ser preenchidos."}, 400

    try:
        max_participantes = int(max_participantes)
    except ValueError:
        return {"erro": "maximo de participantes deve ser um número inteiro."}, 400

    arquivo_foto = request.files.get("arquivo_foto")

    hive_dict, status = Hive_Service.adicionar_hive(
        titulo=titulo,
        descricao=descricao,
        esporte_nome=esporte_nome,
        data_hora_str=data_hora_str,
        localizacao=localizacao,
        endereco=endereco,
        max_participantes=max_participantes,
        privado=privado,
        observacoes=observacoes,
        arquivo_foto=arquivo_foto
    )

    return hive_dict, status


# Implementado
@hive_bp.route('/meusHive', methods=['GET'])
def meus_hive():
    return Hive_Service.listar_MeusHive()


# Implementado
@hive_bp.route('/editarHive', methods=['PUT'])
def EditarHive():

    hive_id = request.form.get("id")

    if not hive_id:
        return jsonify({"erro": "O campo 'id' é obrigatório."}), 400

    campos = [
        "titulo", "descricao", "esporte_nome", "data_hora", "localizacao", "endereco",
        "max_participantes", "privado", "observacoes"
    ]

    dados_hive = {campo: request.form.get(campo) for campo in campos}
    imagem = request.files.get("arquivo_foto")

    resposta, status = Hive_Service.editar_hive_por_id(
        hive_id=hive_id,
        dados=dados_hive,
        imagem=imagem
    )

    return jsonify(resposta), status


# Implementado
@hive_bp.route('/deletarHive', methods=['DELETE'])
def deletar_hive():
    dados = request.get_json()
    
    hive_id = dados.get('hive_id') if dados else None

    if not hive_id:
        return jsonify({"erro": "O campo 'hive_id' é obrigatório."}), 400

    resposta, status = Hive_Service.deletar_hive(str(hive_id))
    return jsonify(resposta), status
