from flask import jsonify, Blueprint, request
from resources.service import cotizacion as cotizacion

config_bp = Blueprint("routes-config", __name__)


@config_bp.route('/configuracion/cotizacion', methods=['GET'])
def get_configuracion_cotizacion():
    return jsonify(cotizacion.prices_db())

