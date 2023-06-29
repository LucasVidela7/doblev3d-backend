from flask import jsonify, Blueprint, request
from resources.service import carrito

carrito_bp = Blueprint("routes-carrito", __name__)


@carrito_bp.route('/carrito', methods=['GET'])
def obtener_carrito():
    hash = request.args.get('hash')
    carr = carrito.obtener_carrito(hash)
    return jsonify(carr)


@carrito_bp.route('/carrito/<int:id_producto>', methods=['DELETE'])
def borrar_del_carrito(id_producto):
    hash = request.args.get('hash')
    carrito.borrar_carrito(hash, id_producto)
    return jsonify({'message': 'Producto eliminado'})


@carrito_bp.route('/carrito', methods=['POST'])
def agregar_carrito():
    body = request.json
    carr = carrito.agregar_carrito(body)

    if carr:
        return jsonify({'message': 'Producto agregado al carrito'})
    else:
        return jsonify({'message': 'Error al agregar producto'}), 417
