from flasgger import swag_from
from flask import request, jsonify, Blueprint

from resources.service import productos as products
from resources.service import piezas as piezas
from resources.service import extras as extras
from resources.service import cotizacion as cotizacion

products_bp = Blueprint("routes-products", __name__)


@products_bp.route('/productos', methods=['POST'])
def add_products():
    id_product = products.insert_product(request.json)
    if id_product:
        return jsonify({"idproducto": id_product}), 201
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['GET'])
def get_product_by_id(id_product):
    if id_product:
        product_details = products.select_product_by_id(id_product)
        list_piezas, cot = cotizacion.get_price_piezas(piezas.select_piezas_by_id_product(id_product))
        list_extras, extra_amount = extras.select_extras_by_id_product(id_product)
        precio_unit = cotizacion.get_precio_unitario(id_product)

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
def all_products():
    return jsonify({"productos": products.get_all_products()})


@products_bp.route('/productos/<int:id_product>', methods=['PUT'])
def update_product(id_product):
    if id_product:
        products.update_product(id_product, request.json)
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>/precio', methods=['POST'])
def insert_product_price(id_product):
    if id_product:
        cotizacion.insert_precio_unitario(id_product, request.json)
        return jsonify({"mensaje": "Precio agregado"})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>/piezas', methods=['GET'])
def productos_piezas(id_product):
    if id_product:
        return jsonify({"piezas": piezas.select_piezas_by_id_product(id_product),
                        "producto": products.select_product_by_id(id_product)})
    return jsonify({"message": "internal server error"})
