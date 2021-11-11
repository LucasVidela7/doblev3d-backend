from flask import request, jsonify, Blueprint
from resources.service import categorias as categories

categorias_bp = Blueprint("routes-categories", __name__)


@categorias_bp.route('/categorias', methods=['GET'])
def all_categories():
    return jsonify({"productos": categories.get_all_categories()})
