import copy
import json
from datetime import datetime

import uuid
from flask import jsonify

from resources.service import extras as extras
from resources.service import cotizacion as cotizacion
from resources.service import estados as estados
from database import utils as db


class estadosVentas:
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN PROCESO"
    TERMINADO = "TERMINADO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


def insertar_preventa(request):
    sql = "delete from preventa where statement_timestamp() - creado > '00:30:00'::interval;"
    db.delete_sql(sql)

    response = request.copy()
    hash = request['hash']

    sql = f"DELETE FROM preventa WHERE hash = '{hash}';"
    db.delete_sql(sql)

    cantidades = {}
    for p in request['productos']:
        id_producto = str(p["id"])
        cantidad = int(p["cantidad"])

        if id_producto not in cantidades:
            cantidades[id_producto] = cantidad
        else:
            cantidades[id_producto] += cantidad

    for p in response['productos']:
        id_producto = str(p["id"])
        cantidad = int(p["cantidad"])
        descuento_adicional = p['descuentoAdicional']
        sumar_descuento = p['sumarDescuento']
        precios = cotizacion.precio_por_cantidad(id_producto, cantidades[id_producto])
        if precios:
            p['preciounitario'] = precios['precioReal']
            p['descuento'] = precios['descuento']
            p['descuentoTotal'] = precios['descuento']
            p['precioUnitarioFinal'] = precios['unidad']
            p['precioTotal'] = round(precios['unidad'] * cantidad, 2)
        else:
            p['preciounitario'] = cotizacion.get_precio_unitario_by_product_id(id_producto)
            p['descuento'] = 0
            p['descuentoTotal'] = 0
            p['precioUnitarioFinal'] = p['preciounitario']
            p['precioTotal'] = round(p['precioUnitarioFinal'] * cantidad, 2)

        if descuento_adicional and sumar_descuento:
            p['descuentoTotal'] += p['descuentoAdicional']
            p['precioUnitarioFinal'] = round((100 - p['descuentoTotal']) * p['preciounitario'] / 100, 2)
            p['precioTotal'] = round(p['precioUnitarioFinal'] * cantidad, 2)
        elif descuento_adicional and not sumar_descuento:
            p['precioUnitarioFinal'] = round((100 - p['descuentoAdicional']) * p['precioUnitarioFinal'] / 100, 2)
            p['precioTotal'] = round(p['precioUnitarioFinal'] * cantidad, 2)
            p['descuentoTotal'] = int(100 - (p['precioUnitarioFinal'] * 100 / p['preciounitario']))

    sql = f"""INSERT INTO preventa (response, hash) VALUES ('{json.dumps(response)}', '{hash}') RETURNING id;"""
    id = db.insert_sql(sql, key='id')
    if not id:
        return {}
    return response


def insertar_venta(request):
    cliente = request['cliente']
    contacto = request['contacto']
    hash = request['hash']

    sql = f"SELECT * FROM preventa WHERE hash = '{hash}'"
    productos = db.select_first(sql)

    if not productos:
        return None

    productos = json.loads(productos['response'])['productos']
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')  # 2021-11-18

    sql = f"""INSERT INTO ventas(cliente,fechaCreacion, contacto, estado)
            VALUES('{cliente}','{fecha_creacion}','{contacto}', '{estadosVentas.PENDIENTE}')   
            RETURNING id;"""
    id_venta = db.insert_sql(sql, key='id')
    if id_venta:
        productos_pedido = []
        for p in productos:
            id_producto = p["id"]
            uuid_item = p["itemId"]
            cantidad = int(p["cantidad"])
            observaciones = str(p.get("observaciones", ""))

            # for x in range(int(p["cantidad"])):
            costo_unidad = cotizacion.get_costo_total(id_producto)
            costo_unidad += extras.select_extras_by_id_product(id_producto)[1]

            # Precio unitario
            descuento = int(p['descuentoTotal'])  # TODO Calcular en base si hay descuento adicional
            precio_unidad = round(p['precioUnitarioFinal'], 2)
            ganancia_unidad = precio_unidad - costo_unidad

            productos_pedido.append([id_venta,
                                     id_producto,
                                     round(costo_unidad, 2),  # Costo unidad
                                     round(costo_unidad * cantidad, 2),  # Costo total
                                     round(ganancia_unidad, 2),  # Ganancia unidad
                                     round(ganancia_unidad * cantidad, 2),  # Ganancia total
                                     round(p['preciounitario'], 2),  # Precio unitario real
                                     precio_unidad,  # Precio unidad con descuento
                                     cantidad,  # Cantidad
                                     descuento,  # Descuento
                                     round(p['precioTotal'], 2),  # Subtotal
                                     round(p['precioTotal'], 2),  # Total
                                     observaciones,
                                     uuid_item])

            sql = (
                f"INSERT INTO ventas_productos_detalle (itemid, idventa, pendiente, idproducto) VALUES ('{uuid_item}', "
                f"'{id_venta}','{cantidad}', {id_producto})")
            db.insert_sql(sql)

        values = ""
        for pp in productos_pedido:
            values += '(' + ",".join(f"'{p}'" for p in pp) + '),'
        sql = f"""INSERT INTO ventas_productos (idventa, idproducto, costounidad, costototal, gananciaunidad, 
                gananciatotal, precioreal, preciounidad, cantidad, descuento, subtotal, total, observaciones, 
                itemid) VALUES {values[:-1]}"""
        db.insert_sql(sql)

        sql = f"DELETE FROM preventa WHERE hash = '{hash}'"
        db.delete_sql(sql)

        return id_venta


def get_ventas_by_product_id(product_id):
    sql = f"select * from ventas_productos where idproducto='{product_id}'"
    return db.select_multiple(sql)


def detalle_venta(_id):
    sql = f"SELECT v.*, (SELECT COALESCE(SUM(pg.monto),0) FROM pagos pg WHERE pg.idventa = v.id) AS senia, " \
          f"(SELECT COALESCE(SUM(vp.total),0) FROM ventas_productos vp WHERE vp.idventa = v.id) AS preciototal " \
          f"FROM ventas AS v WHERE v.id= {_id};"
    venta = db.select_first(sql)

    if not venta:
        return jsonify({"status": False})

    venta["fechacreacion"] = venta["fechacreacion"].strftime('%Y-%m-%d')
    venta.pop("idestado", None)

    # Obtener productos
    sql = f"SELECT vp.cantidad, vp.itemid, vp.idproducto, vp.observaciones, vp.total, vp.preciounidad, " \
          f"CONCAT(cats.categoria, ' - ', p.descripcion) as descripcion FROM ventas_productos AS vp " \
          f"INNER JOIN productos AS p ON vp.idproducto=p.id " \
          f"INNER JOIN categorias AS cats ON cats.id=p.idcategoria " \
          f"WHERE idventa= {_id} " \
          f"ORDER BY vp.id DESC;"
    venta['productos'] = db.select_multiple(sql)

    # DETALLE de items
    sql = (f"SELECT pendiente, imprimiendo, listo, errores, cancelados, itemid "
           f"FROM ventas_productos_detalle where idventa='{_id}'")
    detalles = db.select_multiple(sql)
    detalles = dict(map(lambda x: (x["itemid"], x), detalles))

    for dv in venta['productos']:
        dv['detalle'] = detalles[dv['itemid']]
        del dv['detalle']['itemid']

    return venta


def select_venta_by_id(_id):
    # Obtener venta
    sql = f"SELECT v.*, (SELECT COALESCE(SUM(pg.monto),0) FROM pagos pg WHERE pg.idventa = v.id) AS senia, " \
          f"(SELECT COALESCE(SUM(vp.preciounidad),0) FROM ventas_productos vp WHERE vp.idventa = v.id) AS preciototal " \
          f"FROM ventas AS v WHERE v.id= {_id};"
    venta = db.select_first(sql)

    if not venta:
        return jsonify({"mensaje": "Venta no existe"}), 404

    venta["fechacreacion"] = venta["fechacreacion"].strftime('%Y-%m-%d')
    venta["estado"] = estados.order_estados(estados.get_estados_ventas(), venta["idestado"])
    venta.pop("idestado", None)
    venta["productos"] = []
    venta["resumen"] = []

    # Obtener productos
    sql = f"SELECT vp.*, CONCAT(cats.categoria, ' - ', p.descripcion) as descripcion FROM ventas_productos AS vp " \
          f"INNER JOIN productos AS p ON vp.idproducto=p.id " \
          f"INNER JOIN categorias AS cats ON cats.id=p.idcategoria " \
          f"WHERE idventa= {_id} " \
          f"ORDER BY vp.id DESC;"
    productos = db.select_multiple(sql)

    if venta["estado"]["actual"]["estado"] in ("ENTREGADO", "CANCELADO"):
        sql = f"""
                SELECT count(vp.idproducto) as cantidad, CONCAT(cats.categoria, ' - ', p.descripcion) as descripcion 
                FROM ventas_productos AS vp 
                INNER JOIN productos AS p ON vp.idproducto=p.id 
                INNER JOIN categorias AS cats ON cats.id=p.idcategoria 
                WHERE idventa= '{_id}'
                GROUP BY descripcion, cats.categoria;
                """
        venta["resumen"] = db.select_multiple(sql)
        return jsonify(venta), 200

    # Performance
    estados_productos = estados.get_estados_productos()
    ids_products = list(str(x["idproducto"]) for x in productos)
    sql = f"select * from piezas where idproducto in ({','.join(ids_products)});"
    piezas = db.select_multiple(sql)

    for p in productos:
        p["estado"] = estados.order_estados(copy.deepcopy(estados_productos), p["idestado"])

        # Obtener piezas
        p["piezas"] = [pi for pi in piezas if pi["idproducto"] == p["idproducto"]]
        p.pop("idestado", None)
        p.pop("idventa", None)
        p.pop("idproducto", None)

    venta["productos"] = productos
    return jsonify(venta), 200


def obtener_todas_las_ventas():
    sql = f"SELECT v.*, " \
          f" (SELECT (SELECT COALESCE(SUM(vp.cantidad),0)) FROM ventas_productos vp WHERE vp.idventa = v.id) AS productos, " \
          f" (SELECT sum(vp.total) FROM ventas_productos vp WHERE vp.idventa = v.id) AS precioTotal, " \
          f" (SELECT COALESCE(SUM(pg.monto),0) FROM pagos pg WHERE pg.idventa = v.id) AS senia " \
          f" FROM ventas AS v " \
          f" WHERE estado <>  '{estadosVentas.CANCELADO}'" \
          f" ORDER BY id ASC, senia DESC, productos DESC;"
    ventas = db.select_multiple(sql)
    for v in ventas:
        v["fechacreacion"] = v["fechacreacion"].strftime('%Y-%m-%d')

    aux_ventas = []
    for v in ventas:
        if v["estado"] != "ENTREGADO":
            aux_ventas.append(v)
        elif v["senia"] < v["preciototal"]:
            aux_ventas.append(v)

    return aux_ventas


def detalle_item(id_venta, item_id):
    sql = (f"SELECT pendiente, imprimiendo, listo, errores, cancelados "
           f"FROM ventas_productos_detalle WHERE idventa='{id_venta}' and itemid='{item_id}';")
    return db.select_first(sql)


def modificar_item(id_venta, item_id, request):
    estados = ['pendiente', 'imprimiendo', 'listo']
    estado_anterior = request['estadoAnterior']
    estado_nuevo = request['estadoNuevo']
    cantidad = request['cantidad']

    if estado_anterior not in estados or estado_nuevo not in estados or cantidad < 1 or estado_nuevo == estado_anterior:
        return {}

    item = detalle_item(id_venta, item_id)

    if item[estado_anterior] < cantidad:
        return {}

    sql = (f"UPDATE ventas_productos_detalle SET {estado_anterior} = {estado_anterior} - {cantidad}, "
           f"{estado_nuevo} = {estado_nuevo} + {cantidad} WHERE idventa='{id_venta}' and itemid='{item_id}';")
    db.update_sql(sql)

    return detalle_item(id_venta, item_id)


def registrar_error(id_venta, item_id, cantidad):
    item = detalle_item(id_venta, item_id)
    if item['imprimiendo'] < cantidad and cantidad > 0:
        return {}

    sql = (f"UPDATE ventas_productos_detalle SET errores = errores + {cantidad}, pendiente = pendiente + {cantidad}, "
           f"imprimiendo = imprimiendo - {cantidad} "
           f"WHERE idventa='{id_venta}' and itemid='{item_id}';")
    db.update_sql(sql)
    return detalle_item(id_venta, item_id)


def cancelar_venta(id_venta):
    # Cambiar estado productos
    sql = f"UPDATE ventas SET estado = '{estadosVentas.CANCELADO}' where id='{id_venta}';"
    db.update_sql(sql)
