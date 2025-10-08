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
    endereco = request.form.get("endereco")
    torneio = request.form.get("torneio", "false").lower() == "true"
    premiacao = request.form.get("premiacao", 0)
    link_oficial = request.form.get("link_oficial","")

    if not all([titulo, descricao, esporte_nome, data_hora_str, localizacao, endereco]):
        return {"erro": "Todos os campos obrigatórios devem ser preenchidos."}, 400

    arquivo_foto = request.files.get("arquivo_foto")

    evento_dict, status = Eventos_Service.adicionar_evento(
        titulo=titulo,
        descricao=descricao,
        esporte_nome=esporte_nome,
        data_hora_str=data_hora_str,
        localizacao=localizacao,
        endereco=endereco,
        torneio=torneio,
        premiacao=premiacao,
        arquivo_foto=arquivo_foto,
        link_oficial=link_oficial
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
        "titulo", "descricao", "esporte_nome", "data_hora", "localizacao", "endereco",
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


# Implementado
@evento_bp.route('/participando', methods=['GET'])
def get_eventos_participando():
    return Eventos_Service.listar_eventos_participando()


# Implementado
@evento_bp.route('/pendentes', methods=['POST'])
def listar_pendentes_controller():
    dados = request.get_json()
    
    if not dados or 'evento_id' not in dados:
        return jsonify({"erro": "O campo 'evento_id' é obrigatório."}), 400

    evento_id = dados['evento_id']
    return Eventos_Service.listar_pendentes(evento_id)


# Implementado
@evento_bp.route('/decidirParticipante', methods=['POST'])
def decidir_participante_controller():
    dados = request.get_json()
    evento_id = dados.get("evento_id")
    usuario_id = dados.get("usuario_id")
    acao = dados.get("acao")  

    if not evento_id or not usuario_id or not acao:
        return jsonify({"erro": "Campos 'evento_id', 'usuario_id' e 'acao' são obrigatórios"}), 400

    return Eventos_Service.decidir_participante(evento_id, usuario_id, acao)