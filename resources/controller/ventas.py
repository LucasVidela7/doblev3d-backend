from flask import request, jsonify, Blueprint
from resources.service import ventas as ventas
from resources.service import pagos as pagos
from resources.service.usuarios import token_required

ventas_bp = Blueprint("routes-ventas", __name__)


@ventas_bp.route('/preVenta', methods=['POST'])
@token_required
def pre_venta():
    uuid = ventas.insertar_preventa(request.json)
    if uuid:
        return jsonify({"preVenta": uuid, "status": True})
    return jsonify({"status": False})


@ventas_bp.route('/ventas', methods=['POST'])
@token_required
def add_venta():
    id_venta = ventas.insertar_venta(request.json)
    if id_venta:
        return jsonify({"id": id_venta, "status": True})
    return jsonify({"status": False})


@ventas_bp.route('/ventas', methods=['GET'])
@token_required
def all_ventas():
    list_ventas = ventas.obtener_todas_las_ventas()
    return jsonify({"ventas": list_ventas})


@ventas_bp.route('/ventas/<int:id_venta>/detalle', methods=['GET'])
@token_required
def detalle_venta(id_venta):
    return ventas.detalle_venta(id_venta)


@ventas_bp.route('/ventas/<int:id_venta>/estadoItem/<itemId>', methods=['PUT'])
@token_required
def modificar_item(id_venta, itemId):
    response = ventas.modificar_item(id_venta, itemId, request.json)
    return jsonify({"status": bool(response), "detalle": response})


@ventas_bp.route('/ventas/<int:id_venta>/error/<item_id>', methods=['PUT'])
@token_required
def registrar_error(id_venta, item_id):
    cantidad = request.json['cantidad']
    response = ventas.registrar_error(id_venta, item_id, cantidad)
    return jsonify({"status": bool(response), "detalle": response})


@ventas_bp.route('/ventas/<int:id_venta>', methods=['DELETE'])
@token_required
def cancelar_venta(id_venta):
    ventas.cancelar_venta(id_venta)
    return jsonify({"status": True})


@ventas_bp.route('/ventas/producto/<int:id_producto>', methods=['DELETE'])
@token_required
def cancelar_producto(id_producto):
    return estados.cancelar_producto(id_producto)


@ventas_bp.route('/ventas/<int:id_venta>/pagos', methods=['GET'])
@token_required
def select_pagos_venta(id_venta):
    return jsonify(pagos.get_all_pagos_by_id_venta(id_venta))


@ventas_bp.route('/ventas/<int:id_venta>/entregado', methods=['PUT'])
@token_required
def entregar_venta(id_venta):
    entrega = ventas.entregar_ventas(id_venta)
    return jsonify({"status": entrega})
