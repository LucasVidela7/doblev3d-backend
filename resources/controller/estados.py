from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import estados as estados

estados_bp = Blueprint("routes-estados", __name__)


@estados_bp.route('/estado/producto', methods=['POST'])
def update_estado():
    return estados.cambiar_estado_producto(request.json)
