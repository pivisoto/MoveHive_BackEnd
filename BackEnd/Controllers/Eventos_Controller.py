from flask import Blueprint, jsonify, request
from Services import Eventos_Service

evento_bp = Blueprint('evento_bp', __name__, url_prefix="/evento")

# Implementado
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

    print(titulo, descricao, esporte_nome, data_hora_str, localizacao, max_participantes, torneio, premiacao, privado, observacoes)
    print("oiii")
    
    if not all([titulo, descricao, esporte_nome, data_hora_str, localizacao, max_participantes]):
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



# Implementado
@evento_bp.route('/meusEventos', methods=['GET'])
def meus_eventos():
    return Eventos_Service.listar_eventos_usuario()


@evento_bp.route('/usuario/<string:usuario_id>', methods=['GET'])
def eventos_por_id_usuario(usuario_id):
    return Eventos_Service.listar_eventos_por_id_usuario(usuario_id)


# Implementado
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



# Implementado
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



# Implementado
@evento_bp.route('/listarEventos', methods=['GET'])
def listar_eventos():
    return Eventos_Service.listar_eventos()



# Implementado
@evento_bp.route('/listarTorneios', methods=['GET'])
def listar_torneios():
    return Eventos_Service.listar_torneios()



# Implementado
@evento_bp.route('/participarEvento', methods=['POST'])
def participar_evento():
    dados = request.get_json()
    
    if not dados or 'evento_id' not in dados:
        return jsonify({"erro": "O campo 'evento_id' é obrigatório."}), 400

    evento_id = dados['evento_id']
    
    return Eventos_Service.participar_evento(evento_id)



# Implementado
@evento_bp.route('/cancelarParticipacao', methods=['POST'])
def cancelar_participacao_evento():
    dados = request.get_json()
    
    if not dados or 'evento_id' not in dados:
        return jsonify({"erro": "O campo 'evento_id' é obrigatório."}), 400

    evento_id = dados['evento_id']
    
    return Eventos_Service.cancelar_participacao(evento_id)