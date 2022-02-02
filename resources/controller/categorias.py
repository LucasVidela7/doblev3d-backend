from flasgger import swag_from
from flask import jsonify, Blueprint, request

from resources.service import categorias as categories
from resources.service.usuarios import token_required

categorias_bp = Blueprint("routes-categories", __name__)


@categorias_bp.route('/categorias', methods=['GET'])
@token_required
def all_categories():
    return jsonify({"categorias": categories.get_all_categories()}), 200


@categorias_bp.route('/categorias', methods=['POST'])
@token_required
def add_category():
    id_categoria = categories.add_category(request.json)
    return jsonify({"idcategoria": id_categoria}), 200


@categorias_bp.route('/categorias/<int:id_categoria>', methods=['PUT'])
@token_required
def update_category(id_categoria):
    categories.update_category(id_categoria, request.json)
    return jsonify({"message": "Editado!"}), 200


@categorias_bp.route('/categorias/<int:id_categoria>', methods=['DELETE'])
@token_required
def delete_category(id_categoria):
    return categories.delete_category(id_categoria)
