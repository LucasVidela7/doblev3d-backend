from flask import jsonify, Blueprint, request
from resources.service import catalogo as catalogo

catalogo_bp = Blueprint("routes-catalog", __name__)


@catalogo_bp.route('/catalogo/categorias', methods=['GET'])
def all_catalog_categories():
    return jsonify(catalogo.obtener_categorias_catalogo()), 200


@catalogo_bp.route('/catalogo/productos/<int:id_categoria>', methods=['GET'])
def all_products_by_id_category(id_categoria):
    return jsonify(catalogo.obtener_productos_por_categoria(id_categoria)), 200


@catalogo_bp.route('/catalogo/productos/destacados', methods=['GET'])
def all_featured_products():
    return jsonify(catalogo.obtener_productos_destacados()), 200


@catalogo_bp.route('/catalogo/productos', methods=['GET'])
def all_catalog_products():
    return jsonify(catalogo.obtener_productos_destacados()), 200


@catalogo_bp.route('/catalogo/producto/<int:id_product>', methods=['GET'])
def get_product_catalog_by_id(id_product):
    return jsonify(catalogo.obtener_producto_catalogo(id_product)), 200
