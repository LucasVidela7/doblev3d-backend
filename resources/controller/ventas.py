from flasgger import swag_from
from flask import request, jsonify, Blueprint
from documentation.route import get_doc_path
from resources.service import ventas as ventas
from resources.service import pagos as pagos

ventas_bp = Blueprint("routes-ventas", __name__)


@ventas_bp.route('/ventas', methods=['POST'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def add_venta():
    id_venta = ventas.insertar_venta(request.json)
    if id_venta:
        return jsonify({"idVenta": id_venta})
    return jsonify({"message": "internal server error"})


@ventas_bp.route('/ventas', methods=['GET'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def all_ventas():
    list_ventas = ventas.get_all_ventas()
    return jsonify({"ventas": list_ventas})


@ventas_bp.route('/ventas/<int:id_venta>', methods=['GET'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def select_venta(id_venta):
    venta = ventas.select_venta_by_id(id_venta)
    return jsonify(venta)


@ventas_bp.route('/ventas/<int:id_venta>/pagos', methods=['GET'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def select_pagos_venta(id_venta):
    return jsonify(pagos.get_all_pagos_by_id_venta(id_venta))
