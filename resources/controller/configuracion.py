from flask import jsonify, Blueprint, request
from resources.service import cotizacion as cotizacion

config_bp = Blueprint("routes-config", __name__)


@config_bp.route('/configuracion/cotizacion', methods=['GET'])
def get_configuracion_cotizacion():
    return jsonify(cotizacion.prices_db())


@config_bp.route('/configuracion/cotizacion', methods=['PUT'])
def edit_configuracion_cotizacion():
    cotizacion.update_prices(request.json)
    return jsonify({"mensaje": "Editado"})
