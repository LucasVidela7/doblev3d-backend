from flask import jsonify, Blueprint
from resources.service import categorias as categories
from resources.service.usuarios import token_required

categorias_bp = Blueprint("routes-categories", __name__)


@categorias_bp.route('/categorias', methods=['GET'])
# @token_required
def all_categories():
    return jsonify({"productos": categories.get_all_categories()}), 200
