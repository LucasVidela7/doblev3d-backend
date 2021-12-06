from flasgger import swag_from
from flask import request, jsonify, Blueprint

from documentation.route import get_doc_path
from resources.service import productos as products
from resources.service import piezas as piezas
from resources.service import extras as extras
from resources.service import cotizacion as cotizacion

products_bp = Blueprint("routes-products", __name__)


@products_bp.route('/productos', methods=['POST'])
@swag_from(get_doc_path("productos/post_productos.yml"))
def add_products():
    id_product = products.insert_product(request.json)
    if id_product:
        return jsonify({"idproducto": id_product})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['GET'])
@swag_from(get_doc_path("productos/get_product_by_id.yml"))
def get_product_by_id(id_product):
    if id_product:
        product_details = products.select_product_by_id(id_product)
        list_piezas, cot = cotizacion.get_price_piezas(piezas.select_piezas_by_id_product(id_product))
        list_extras, extra_amount = extras.select_extras_by_id_product(id_product)
        costo_total = round(cot["costoElaboracion"] + extra_amount, 2)
        precio_unit = cotizacion.get_precio_unitario(id_product)
        precio_unit = cotizacion.check_precio_unitario(precio_unit, costo_total)

        response = {
            "producto": product_details,
            "piezas": list_piezas,
            "totalExtras": extra_amount,
            "extras": list_extras,
            "cotizacionTotal": cot,
            "precio": precio_unit
        }
        return jsonify(response)
    return jsonify({"message": "internal server error"}), 500


@products_bp.route('/productos', methods=['GET'])
@swag_from(get_doc_path("productos/get_productos.yml"))
def all_products():
    return jsonify({"productos": products.get_all_products()})


@products_bp.route('/productos/<int:id_product>', methods=['PUT'])
@swag_from(get_doc_path("productos/put_product.yml"))
def update_product(id_product):
    if id_product:
        products.update_product(id_product, request.json)
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>/precio', methods=['POST'])
# @swag_from(get_doc_path("productos/put_product.yml"))
def insert_product_price(id_product):
    if id_product:
        cotizacion.insert_precio_unitario(id_product, request.json)
        return jsonify({"mensaje": "Precio agregado"})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>/piezas', methods=['GET'])
# @swag_from(get_doc_path("productos/put_product.yml"))
def productos_piezas(id_product):
    if id_product:
        return jsonify({"piezas": piezas.select_piezas_by_id_product(id_product)})
    return jsonify({"message": "internal server error"})
