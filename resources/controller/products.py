import os

from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import products as products
from resources.service import piezas as piezas

products_bp = Blueprint("routes-products", __name__)


@products_bp.route('/productos', methods=['POST'])
def add_products():
    id_product = products.insert_product(request.json)
    if id_product:
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos', methods=['GET'])
@swag_from(os.getcwd() + "\documentation\get_productos.yml")
def all_products():
    return jsonify({"productos": products.get_all_products()})


@products_bp.route('/productos/<int:id_product>', methods=['GET'])
def get_product_by_id(id_product):
    if id_product:
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['PUT'])
def update_product(id_product):
    if id_product:
        products.update_product(id_product, request.json)
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})
