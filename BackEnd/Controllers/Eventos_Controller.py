from flask import Blueprint, jsonify, request
from Services import Eventos_Service

evento_bp = Blueprint('evento_bp', __name__, url_prefix="/evento")


@evento_bp.route('/AdicionarEvento', methods=['POST'])
def criar_evento():
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    esporte_nome = request.form.get("esporte_nome")
    data_hora_str = request.form.get("data_hora_str")
    localizacao = request.form.get("localizacao")
    max_participantes = request.form.get("max_participantes")
    torneio = request.form.get("torneio", "false").lower() == "true"
    premiacao = request.form.get("premiacao", 0)
    privado = request.form.get("privado", "false").lower() == "true"
    observacoes = request.form.get("observacoes", "")

    if not all([titulo, descricao, esporte_nome, data_hora_str, localizacao, max_participantes, torneio, privado]):
        return {"erro": "Todos os campos obrigatórios devem ser preenchidos."}, 400

    try:
        max_participantes = int(max_participantes)
    except ValueError:
        return {"erro": "max_participantes deve ser um número inteiro."}, 400

    arquivo_foto = request.files.get("arquivo_foto")

    evento_dict, status = Eventos_Service.adicionar_evento(
        titulo=titulo,
        descricao=descricao,
        esporte_nome=esporte_nome,
        data_hora_str=data_hora_str,
        localizacao=localizacao,
        max_participantes=max_participantes,
        torneio=torneio,
        premiacao=premiacao,
        privado=privado,
        observacoes=observacoes,
        arquivo_foto=arquivo_foto
    )

    return evento_dict, status


@evento_bp.route('/meusEventos', methods=['GET'])
def meus_eventos():
    return Eventos_Service.listar_eventos_usuario()


@evento_bp.route('/editarEvento', methods=['PUT'])
def EditarEvento():

    evento_id = request.form.get("id")

    if not evento_id:
        return jsonify({"erro": "O campo 'id' é obrigatório."}), 400

    # Coleta os campos do formulário
    campos = [
        "titulo", "descricao", "esporte_nome", "data_hora", "localizacao",
        "max_participantes", "torneio", "premiacao", "privado", "observacoes"
    ]

    dados_evento = {campo: request.form.get(campo) for campo in campos}
    imagem = request.files.get("arquivo_foto")

    # Chamada ao service
    resposta, status = Eventos_Service.editar_evento_por_id(
        evento_id=evento_id,
        dados=dados_evento,
        imagem=imagem
    )

    return jsonify(resposta), status


@evento_bp.route('/deletarEvento', methods=['DELETE'])
def deletar_evento_controller():
    # Obtém os dados do corpo da requisição JSON
    dados = request.get_json()
    
    # Verifica se os dados foram enviados e extrai o evento_id
    evento_id = dados.get('evento_id') if dados else None

    if not evento_id:
        return jsonify({"erro": "O campo 'evento_id' é obrigatório."}), 400

    # Converte para string para garantir compatibilidade, se necessário
    resposta, status = Eventos_Service.deletar_evento(str(evento_id))
    return jsonify(resposta), status