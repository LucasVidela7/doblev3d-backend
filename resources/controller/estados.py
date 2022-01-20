from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import estados as estados

estados_bp = Blueprint("routes-estados", __name__)


# @estados_bp.route('/estado/pieza', methods=['POST'])
# # @swag_from(get_doc_path("productos/post_productos.yml"))
# def update_estado():
#     return estados.cambiar_estado_pieza(request.json)
