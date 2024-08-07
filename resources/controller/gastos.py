from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import gastos as gastos
from resources.service.usuarios import token_required

gastos_bp = Blueprint("routes-gastos", __name__)


@gastos_bp.route('/gastos', methods=['POST'])
@token_required
def add_gastos():
    gastos.insertar_gastos(request.json)
    return jsonify({"gastos": gastos.get_gastos()})


@gastos_bp.route('/gastos', methods=['GET'])
@token_required
def all_gastos():
    mes = request.args.get('mes')
    anio = request.args.get('anio')
    return jsonify({"gastos": gastos.get_gastos(mes=mes, anio=anio)})


@gastos_bp.route('/gastos/<int:id_gasto>', methods=['DELETE'])
@token_required
def delete_gasto(id_gasto):
    gastos.borrar_gasto(id_gasto)
    return jsonify({"mensaje": "Gasto borrado"})
