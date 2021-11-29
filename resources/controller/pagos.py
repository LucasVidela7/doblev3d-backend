from flasgger import swag_from
from flask import request, jsonify, Blueprint
from documentation.route import get_doc_path
from resources.service import pagos as pagos

pagos_bp = Blueprint("routes-pagos", __name__)


@pagos_bp.route('/pagos', methods=['POST'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def add_pago():
    id_pago = pagos.insertar_pago(request.json)
    if id_pago:
        return jsonify({"idPago": id_pago})
    return jsonify({"message": "internal server error"}), 500


@pagos_bp.route('/pagos', methods=['GET'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def all_pagos():
    return jsonify({"pagos": pagos.get_all_pagos()})


@pagos_bp.route('/mediosDePago', methods=['GET'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def all_medios_de_pagos():
    return jsonify({"mediosDePago": pagos.get_all_medios_pago()})
