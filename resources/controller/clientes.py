from flask import jsonify, Blueprint, request
from resources.service import clientes
from flasgger.utils import swag_from

from resources.service.clientes import token_cliente_required

clientes_bp = Blueprint("routes-clientes", __name__)


@clientes_bp.route('/clientes/login', methods=['POST'])
def login():
    return clientes.login(request.json)


@clientes_bp.route('/clientes/registro', methods=['POST'])
def registro():
    return clientes.registro(request.json)


@clientes_bp.route('/clientes/datos', methods=['GET'])
@token_cliente_required
def datos_clientes(user_id):
    return clientes.datos(user_id)


@clientes_bp.route('/clientes/datos', methods=['PUT'])
@token_cliente_required
def guardar_datos_clientes(user_id):
    body = request.json
    clientes.guardar_datos(user_id, body)
    return jsonify({'message': 'Tus datos se guardaron correctamente'})
