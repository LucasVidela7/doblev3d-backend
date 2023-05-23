from flask import jsonify, Blueprint, request
from resources.service import catalogo as catalogo, cotizacion
from resources.service import productos as products
from resources.service.ventas import get_ventas_by_product_id

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
    if id_product:
        product_details = products.select_product_by_id(id_product)
        precio_unit = cotizacion.get_precio_unitario(id_product)

        response = {
            "producto": product_details,
            "precio": precio_unit['preciounitario'],
            "ventas": bool(get_ventas_by_product_id(id_product))
        }
        return jsonify(response)
    return jsonify({"message": "internal server error"}), 500
