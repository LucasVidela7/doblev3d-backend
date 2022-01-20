from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import gastos as gastos

gastos_bp = Blueprint("routes-gastos", __name__)


@gastos_bp.route('/gastos', methods=['POST'])
def add_gastos():
    gastos.insertar_gastos(request.json)
    return jsonify({"gastos": gastos.get_gastos()})


@gastos_bp.route('/gastos', methods=['GET'])
def all_gastos():
    mes = request.args.get('mes')
    anio = request.args.get('anio')
    return jsonify({"gastos": gastos.get_gastos(mes=mes, anio=anio)})


@gastos_bp.route('/gastos/<int:id_gasto>', methods=['DELETE'])
def delete_gasto(id_gasto):
    gastos.borrar_gasto(id_gasto)
    return jsonify({"mensaje": "Gasto borrado"})
