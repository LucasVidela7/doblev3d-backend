from flasgger import swag_from
from flask import jsonify, Blueprint, request

from documentation.route import get_doc_path
from resources.service import categorias as categories
from resources.service.usuarios import token_required

categorias_bp = Blueprint("routes-categories", __name__)


@categorias_bp.route('/categorias', methods=['GET'])
@swag_from(get_doc_path("get_categorias.yml"))
# @token_required
def all_categories():
    return jsonify({"productos": categories.get_all_categories()}), 200


@categorias_bp.route('/categorias', methods=['POST'])
@swag_from(get_doc_path("post_categorias.yml"))
# @token_required
def add_category():
    id_categoria = categories.add_category(request.json)
    return jsonify({"idcategoria": id_categoria}), 200


@categorias_bp.route('/categorias/<int:id_categoria>', methods=['PUT'])
@swag_from(get_doc_path("put_categorias.yml"))
# @token_required
def update_category(id_categoria):
    categories.update_category(id_categoria, request.json)
    return jsonify({"message": "Editado!"}), 200
