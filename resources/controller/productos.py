from flasgger import swag_from
from flask import request, jsonify, Blueprint

from documentation.route import get_doc_path
from resources.service import productos as products
from resources.service import piezas as piezas
from resources.service import extras as extras
from resources.service import cotizacion as cotizacion

products_bp = Blueprint("routes-products", __name__)


@products_bp.route('/productos', methods=['POST'])
@swag_from(get_doc_path("post_productos.yml"))
def add_products():
    id_product = products.insert_product(request.json)
    if id_product:
        return jsonify({"idproducto": id_product})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['GET'])
@swag_from(get_doc_path("get_product_by_id.yml"))
def get_product_by_id(id_product):
    if id_product:
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        list_piezas_price, cot = cotizacion.get_price_piezas(list_piezas)
        list_extras = extras.select_extras_by_id(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas, "extras": list_extras, "cotizacion": cot})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos', methods=['GET'])
@swag_from(get_doc_path("get_productos.yml"))
def all_products():
    return jsonify({"productos": products.get_all_products()})


@products_bp.route('/productos/<int:id_product>', methods=['PUT'])
@swag_from(get_doc_path("put_product.yml"))
def update_product(id_product):
    if id_product:
        products.update_product(id_product, request.json)
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})
