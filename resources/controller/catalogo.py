from flask import jsonify, Blueprint, request
from resources.service import catalogo as catalogo

catalogo_bp = Blueprint("routes-catalog", __name__)


@catalogo_bp.route('/catalogo/categorias', methods=['GET'])
def all_catalog_categories():
    return jsonify({"categorias": catalogo.get_all_categories_for_catalog()}), 200


@catalogo_bp.route('/catalogo/productos/<int:id_categoria>', methods=['GET'])
def all_products_by_id_category(id_categoria):
    return jsonify({"productos": catalogo.get_all_products_for_catalog(id_categoria)}), 200


@catalogo_bp.route('/catalogo/productos/destacados', methods=['GET'])
def all_featured_products(id_categoria):
    return jsonify({"productos": catalogo.get_all_products_for_catalog(id_categoria)}), 200
