from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import ofertas
from resources.service.usuarios import token_required

ofertas_bp = Blueprint("routes-ofertas", __name__)


@ofertas_bp.route('/ofertas', methods=['GET'])
@token_required
def get_ofertas():
    return jsonify(ofertas.get_ofertas())


@ofertas_bp.route('/ofertas/tipos', methods=['GET'])
@token_required
def get_tipos_ofertas():
    return jsonify(ofertas.get_tipo_ofertas())


@ofertas_bp.route('/ofertas', methods=['POST'])
@token_required
def crear_oferta():
    body = request.json
    tipo = body.get('tipoOferta', False)

    if not tipo:
        response = False
    elif tipo == 'TIENDA':
        response = ofertas.crear_oferta_tienda(body['fechaDesde'],
                                               body['fechaHasta'] + ' 23:59:59',
                                               body['porcentaje'],
                                               body['label'],
                                               body.get('login', False))
    elif tipo == 'CATEGORIA':
        response = ofertas.crear_oferta_categoria(body['fechaDesde'],
                                                  body['fechaHasta'] + ' 23:59:59',
                                                  body['porcentaje'],
                                                  body['idCategoria'],
                                                  body['label'],
                                                  body.get('login', False))
    else:
        response = False

    if response:
        return jsonify({"message": "Oferta creada con éxito"})
    else:
        return jsonify({"message": "Algo falló al crear oferta"}), 417
