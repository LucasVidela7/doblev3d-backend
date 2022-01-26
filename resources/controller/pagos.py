from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import pagos as pagos
from resources.service.usuarios import token_required

pagos_bp = Blueprint("routes-pagos", __name__)


@pagos_bp.route('/pagos', methods=['POST'])
@token_required
def add_pago():
    id_pago = pagos.insertar_pago(request.json)
    if id_pago:
        return jsonify({"idPago": id_pago})
    return jsonify({"message": "internal server error"}), 500


@pagos_bp.route('/pagos', methods=['GET'])
@token_required
def all_pagos():
    mes = request.args.get('mes')
    anio = request.args.get('anio')
    return jsonify({"pagos": pagos.get_all_pagos(mes=mes, anio=anio)})


@pagos_bp.route('/pagos/<int:id_pago>', methods=['DELETE'])
@token_required
def delete_pago(id_pago):
    pagos.borrar_pago(id_pago)
    return jsonify({"pagos": "Pago borrado"})


@pagos_bp.route('/mediosDePago', methods=['GET'])
@token_required
def all_medios_de_pagos():
    return jsonify({"mediosDePago": pagos.get_all_medios_pago()})
