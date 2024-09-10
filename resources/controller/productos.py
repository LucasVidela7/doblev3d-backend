import threading

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
def agregar_producto():
    id_product = products.insert_product(request.json)
    if id_product:
        return jsonify({"idproducto": id_product})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['GET'])
@token_required
def obtener_producto_por_id(id_product):
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
def obtener_productos():
    return jsonify({"productos": products.get_all_products()})


@products_bp.route('/productos/<int:id_product>', methods=['PUT'])
@token_required
def actualizar_producto(id_product):
    if id_product:
        products.update_product(id_product, request.json)
        product_details = products.select_product_by_id(id_product)
        list_piezas = piezas.select_piezas_by_id_product(id_product)
        return jsonify({"producto": product_details, "piezas": list_piezas})
    return jsonify({"message": "internal server error"})


@products_bp.route('/productos/<int:id_product>', methods=['DELETE'])
@token_required
def borrar_producto(id_product):
    return products.delete_product(id_product)


@products_bp.route('/productos/<int:id_product>/imagen', methods=['POST'])
@token_required
def agregar_imagen_producto(id_product):
    # base = request.json["imagen"]
    file = request.files
    imagen = products.upload_image(file, id_product)

    def tinify(**kwargs):
        url = kwargs.get('url')
        id_producto = kwargs.get('id_producto')
        products.tinypng(url, id_producto)

    if imagen:
        thread = threading.Thread(target=tinify, kwargs={'url': imagen, 'id_producto': id_product})
        thread.start()

    return {"status": bool(imagen), "imagen": imagen}, 200


@products_bp.route('/productos/<int:id_product>/imagen', methods=['DELETE'])
@token_required
def eliminar_imagen_producto(id_product):
    products.eliminar_imagen_producto(id_product)
    return {'status': True}


@products_bp.route('/productos/<int:id_product>/precio', methods=['POST'])
@token_required
def insertar_precio_producto(id_product):
    cotizacion.insert_precio_unitario(id_product, request.json["preciounitario"])
    return jsonify({"status": True})


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
    minimo = int(request.args.get('minimo', 5))
    maximo = int(request.args.get('maximo', 100))
    return jsonify(cotizacion.precios_por_mayor(id_product, unidades_minimas=minimo, unidades_maximas=maximo))


@products_bp.route('/productos/<int:id_product>/precioPorCantidad', methods=['POST'])
@token_required
def precio_por_cantidad(id_product):
    cantidad = request.json['cantidad']
    precio = cotizacion.precio_por_cantidad(id_product, cantidad)
    return jsonify({'status': bool(precio), 'precio': precio})


@products_bp.route('/productos/revisar', methods=['GET'])
@token_required
def revisar_productos():
    for p in products.get_all_products():
        cotizacion.get_precio_unitario(p['id'])

    return jsonify({"message": "Proceso terminado"}), 200


@products_bp.route('/productos/actualizarPrecios', methods=['GET'])
@token_required
def actualizar_precios_productos():
    for p in products.get_all_products():
        cotizacion.get_precio_unitario(p['id'], actualizar=True)

    return jsonify({"message": "Proceso terminado"}), 200
