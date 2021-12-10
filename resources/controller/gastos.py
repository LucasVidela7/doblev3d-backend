from flasgger import swag_from
from flask import request, jsonify, Blueprint
from documentation.route import get_doc_path
from resources.service import gastos as gastos

gastos_bp = Blueprint("routes-gastos", __name__)


@gastos_bp.route('/gastos', methods=['POST'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def add_gastos():
    gastos.insertar_gastos(request.json)
    return jsonify({"gastos": gastos.get_gastos()})


@gastos_bp.route('/gastos', methods=['GET'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def all_gastos():
    return jsonify({"gastos": gastos.get_gastos()})


@gastos_bp.route('/gastos/<int:id_gasto>', methods=['DELETE'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def delete_gasto(id_gasto):
    gastos.borrar_gasto(id_gasto)
    return jsonify({"mensaje": "Gasto borrado"})
