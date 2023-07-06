from flask import jsonify, Blueprint, request
from resources.service import carrito
from resources.service.clientes import token_cliente_required

carrito_bp = Blueprint("routes-carrito", __name__)


@carrito_bp.route('/carrito', methods=['GET'])
@token_cliente_required(opcional=True)
def obtener_carrito(user_id):
    if user_id:
        carr = carrito.obtener_carrito_by_user_id(user_id)
    else:
        hash = request.args.get('hash')
        carr = carrito.obtener_carrito_by_hash(hash)
    return jsonify(carr)


@carrito_bp.route('/carrito/<int:id_producto>', methods=['DELETE'])
@token_cliente_required(opcional=True)
def borrar_del_carrito(id_producto, user_id):
    if user_id:
        carrito.borrar_carrito(id_producto, user_id=user_id)
    else:
        hash = request.args.get('hash')
        carrito.borrar_carrito(id_producto, hash=hash)
    return jsonify({'message': 'Producto eliminado'})


@carrito_bp.route('/carrito', methods=['POST'])
@token_cliente_required(opcional=True)
def agregar_carrito(user_id):
    body = request.json
    id_producto = body.get('idProducto', False)
    cantidad = body.get('cantidad', 1)
    hash = body.get('hash', False)

    if user_id:
        carr = carrito.agregar_carrito(id_producto, cantidad, user_id=user_id)
    else:
        carr = carrito.agregar_carrito(id_producto, cantidad, hash=hash)

    if carr:
        return jsonify({'message': 'Producto agregado al carrito'})
    else:
        return jsonify({'message': 'Error al agregar producto'}), 417
