from flasgger import swag_from
from flask import request, jsonify, Blueprint
from documentation.route import get_doc_path
from resources.service import estados as estados

estados_bp = Blueprint("routes-estados", __name__)


@estados_bp.route('/estado/pieza', methods=['POST'])
# @swag_from(get_doc_path("productos/post_productos.yml"))
def update_estado():
    estado = estados.cambiar_estado_pieza(request.json)
    return jsonify({"estado": estado})