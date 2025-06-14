from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from middlewares.auth_token import token_required

import Services.Eventos_Service as eventos_services


evento_bp = Blueprint('evento_bp', __name__, url_prefix="/eventos")


# Função para String -> DateTime
def parse_datetime_from_iso(dt_string):
    if not dt_string:
        return None
    try:
        dt_object = datetime.fromisoformat(dt_string)
        if dt_object.tzinfo is None:
            return dt_object.replace(tzinfo=timezone.utc)
        return dt_object.astimezone(timezone.utc)
    except ValueError:
        return None




@evento_bp.route('/AdicionarEvento', methods=['POST'])
@token_required
def adicionar_evento_route():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Dados do evento não fornecidos"}), 400


    titulo = data.get('titulo')
    descricao = data.get('descricao')
    esporte_id = data.get('esporte_id')
    nivel_esporte = data.get('nivel_esporte')
    localizacao = data.get('localizacao')
    data_hora_str = data.get('data_hora') 
    max_participantes = data.get('max_participantes')
    visibilidade = data.get('visibilidade')


    data_hora_dt = parse_datetime_from_iso(data_hora_str)
    if data_hora_dt is None and data_hora_str is not None and data_hora_str != '':
         return jsonify({"erro": "'data_hora' inválida. Use formato ISO 8601 (ex: '2023-10-27T10:00:00Z')"}), 400
    

    if not isinstance(max_participantes, int) or max_participantes < 1:
         return jsonify({"erro": "'max_participantes' deve ser um número inteiro positivo"}), 400
    

    if not isinstance(localizacao, dict):
        return jsonify({"erro": "'localizacao' deve ser um objeto JSON (dicionário)"}), 400
    

    if not all(key in localizacao for key in ['Estado', 'Cidade', 'Localizacao']):
        return jsonify({"erro": "'localizacao' deve conter as chaves 'Estado', 'Cidade' e 'Localização'"}), 400

      
    resposta, status = eventos_services.adicionar_evento(
        esporte_id=esporte_id,
        titulo=titulo,
        localizacao=localizacao,
        data_hora=data_hora_dt,
        descricao=descricao,
        max_participantes=max_participantes,
        nivel_esporte=nivel_esporte,
        visibilidade=visibilidade
    )

    return jsonify(resposta), status



@evento_bp.route('/ListarEvento', methods=['GET'])
def listarEventos():
    try:
        eventos = eventos_services.listar_eventos()
        return jsonify(eventos), 200
    except Exception as e:
        print(f"Erro na rota listar_eventos_route: {e}")
        return jsonify({"erro": "Erro interno ao listar eventos"}), 500





@evento_bp.route('/BuscarEventoID/<evento_id>', methods=['GET'])
def buscarEventoID(evento_id):
    resposta, status = eventos_services.buscar_evento_por_id(evento_id)
    return jsonify(resposta), status



@evento_bp.route('/AtualizarEvento/<evento_id>', methods=['PUT'])
def atualizarEventoID(evento_id):
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"erro": "Requisição inválida: JSON não fornecido ou mal formatado"}), 400

    if not data:
        return jsonify({"erro": "Nenhum dado para atualizar fornecido"}), 400


    esporte_id = data.get('esporte_id')
    nome = data.get('nome')
    localizacao = data.get('localizacao')
    data_hora_str = data.get('data_hora')
    descricao = data.get('descricao')
    max_participantes = data.get('max_participantes')
    status_evento = data.get('status_evento')
    nivel_esporte = data.get('nivel_esporte')
    link_oficial = data.get('link_oficial')
    tipo_evento = data.get('tipo_evento')
    inscricoes_ativas = data.get('inscricoes_ativas')
    participantes = data.get('participantes')


    data_hora_dt = None
    if data_hora_str is not None:
        data_hora_dt = parse_datetime_from_iso(data_hora_str)
        if data_hora_dt is None: 
            return jsonify({"erro": "'data_hora' inválida. Use formato ISO 8601 (ex: '2023-10-27T10:00:00Z')"}), 400


    if max_participantes is not None: 
         if not isinstance(max_participantes, int) or max_participantes < 1:
              return jsonify({"erro": "'max_participantes' deve ser um número inteiro positivo se fornecido"}), 400
         
         


    updates = {}
    if esporte_id is not None: updates['esporte_id'] = esporte_id 
    if nome is not None: updates['nome'] = nome
    if localizacao is not None: updates['localizacao'] = localizacao
    if data_hora_dt is not None: updates['data_hora'] = data_hora_dt
    if descricao is not None: updates['descricao'] = descricao
    if max_participantes is not None: updates['max_participantes'] = max_participantes
    if status_evento is not None: updates['status_evento'] = status_evento
    if nivel_esporte is not None: updates['nivel_esporte'] = nivel_esporte
    if link_oficial is not None: updates['link_oficial'] = link_oficial
    if tipo_evento is not None: updates['tipo_evento'] = tipo_evento
    if inscricoes_ativas is not None: updates['inscricoes_ativas'] = inscricoes_ativas
    if participantes is not None: updates['participantes'] = participantes


    if not updates:
         return {"status": "sucesso", "mensagem": "Nenhum campo para atualizar foi fornecido"}, 200

    resposta, status = eventos_services.atualizar_evento(evento_id=evento_id, **updates) 

    return jsonify(resposta), status


@evento_bp.route('/ExcluirEventoID/<evento_id>', methods=['DELETE'])
def excluirEventoID(evento_id):
    resposta, status = eventos_services.excluir_evento(evento_id)
    return jsonify(resposta), status