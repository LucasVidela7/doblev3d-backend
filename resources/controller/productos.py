from flasgger import swag_from
from flask import request, jsonify, Blueprint

from resources.service import productos as products
from resources.service import piezas as piezas
from resources.service import extras as extras
from resources.service import cotizacion as cotizacion
from resources.service.usuarios import token_required
from resources.service.ventas import get_ventas_by_product_id

products_bp = Blueprint("routes-products", __name__)


@products_bp.route('/productos', methods=['POST'])
@token_required
def add_products():
    id_product = products.insert_product(request.json)
    if id_product:
        return jsonify({"idproducto": id_product})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['GET'])
@token_required
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
            "precio": precio_unit,
            "ventas": bool(get_ventas_by_product_id(id_product))
        }
        return jsonify(response)
    return jsonify({"message": "internal server error"}), 500


@products_bp.route('/productos', methods=['GET'])
@token_required
def all_products():
    return jsonify({"productos": products.get_all_products()})


@products_bp.route('/productos/<int:id_product>', methods=['PUT'])
@token_required
def update_product(id_product):
    if id_product:
        products.update_product(id_product, request.json)
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['DELETE'])
@token_required
def delete_product(id_product):
    return products.delete_product(id_product)


@products_bp.route('/productos/<int:id_product>/imagen', methods=['POST'])
@token_required
def imagen_producto(id_product):
    # base = request.json["imagen"]
    file = request.files
    return products.upload_image(file, id_product)


@products_bp.route('/productos/imagenes/resize', methods=['GET'])
# @token_required
def imagen_tamano():
    return products.resize_image()


@products_bp.route('/productos/<int:id_product>/precio', methods=['POST'])
@token_required
def insert_product_price(id_product):
    if id_product:
        cotizacion.insert_precio_unitario(id_product, request.json["preciounitario"])
        return jsonify({"mensaje": "Precio agregado"})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>/piezas', methods=['GET'])
@token_required
def productos_piezas(id_product):
    if id_product:
        return jsonify({"piezas": piezas.select_piezas_by_id_product(id_product),
                        "producto": products.select_product_by_id(id_product)})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>/precios', methods=['GET'])
@token_required
def precios_por_mayor(id_product):
    if id_product:
        minimo = int(request.args.get('minimo', 20))
        maximo = int(request.args.get('maximo', 100))
        return jsonify(cotizacion.precios_por_mayor(id_product, unidades_minimas=minimo, unidades_maximas=maximo))

    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/revisar', methods=['GET'])
@token_required
def revisar_productos():
    for p in products.get_all_products():
        cotizacion.get_precio_unitario(p['id'])

    return jsonify({"message": "Proceso terminado"}), 200
