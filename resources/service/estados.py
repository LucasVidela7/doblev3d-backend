import math

from flask import jsonify

from database import utils as db


def get_estados_ventas():
    sql = f"select id, estado, saltear, icono from estados where ventas = '1';"
    return db.select_multiple(sql)


def get_estados_productos():
    sql = f"select id, estado, saltear, icono from estados where productos = '1';"
    return db.select_multiple(sql)


def get_estados_piezas():
    sql = f"select id, estado, saltear, icono from estados where piezas = '1';"
    return db.select_multiple(sql)


def get_id_estado_cancelado():
    sql = "SELECT id FROM estados ORDER BY id DESC LIMIT 1;"
    return db.select_first(sql)["id"]


def order_estados(dictionary, actual_id_estado):
    # dictionary = dict(map(lambda x: (x["id"], x), dictionary))
    estados = {}
    for n, d in enumerate(dictionary):
        if d["id"] == actual_id_estado:
            estados["actual"] = d
            estados["actual"].pop("saltear")
            estados["siguientes"] = []
            estados["anterior"] = {}

            if (n - 1) >= 0:
                estados["anterior"] = dictionary[n - 1]
                estados["anterior"].pop("saltear")

            try:
                if actual_id_estado == dictionary[-1]["id"] or dictionary[n + 1]["id"] == dictionary[-1]["id"]:
                    continue

                estados["siguientes"].append(dictionary[n + 1])
                if dictionary[n + 1]["saltear"] == '1':
                    estados["siguientes"].append(dictionary[n + 3])
                    estados["siguientes"][0].pop("saltear")
                    estados["siguientes"][1].pop("saltear")
            except:
                estados["siguientes"] = []

    return estados


def set_estados_venta(actual_id_estado):
    estados = get_estados_ventas()
    return order_estados(estados, actual_id_estado)


def cambiar_estado_pieza(request):
    id_pieza = request["idPieza"]  # Pieza asociada al producto de la venta
    nuevo_estado = request["idEstado"]

    estados_ventas = [v["id"] for v in get_estados_ventas()]
    estados_productos = [p["id"] for p in get_estados_productos()]
    estados_piezas = [pi["id"] for pi in get_estados_piezas()]

    if nuevo_estado in estados_piezas:

        # Cambiar estado pieza
        sql = f"update ventas_productos_piezas set idestado='{nuevo_estado}' " \
              f"where id='{id_pieza}' RETURNING idproductoventa;"
        id_producto_venta = db.update_sql(sql, key='idproductoventa')

        # Verificar el estado del producto
        sql = f"select min(idestado) as estados_piezas from ventas_productos_piezas " \
              f"where idproductoventa='{id_producto_venta}';"
        nuevo_estado_producto = round(db.select_first(sql)["estados_piezas"])
        if abs(nuevo_estado_producto - nuevo_estado) == 1:
            nuevo_estado_producto = nuevo_estado
        elif nuevo_estado_producto not in estados_productos:
            for n, ep in enumerate(estados_productos):
                if ep < nuevo_estado_producto and n > 0:
                    nuevo_estado_producto = ep
                    break

        # Cambiar estado producto
        sql = f"update ventas_productos set idestado='{nuevo_estado_producto}' " \
              f"where id='{id_producto_venta}' RETURNING idventa;"
        id_venta = db.update_sql(sql, key='idventa')

        # Verificar estado venta
        sql = f"select AVG(idestado) as estados_productos from ventas_productos " \
              f"where idventa='{id_venta}';"
        nuevo_estado_venta = int(db.select_first(sql)["estados_productos"])
        if nuevo_estado_venta not in estados_ventas:
            for n, ev in enumerate(estados_ventas):
                if ev < nuevo_estado_venta and n > 0:
                    nuevo_estado_venta = ev
                    break

        # Cambiar estado venta
        sql = f"update ventas set idestado='{nuevo_estado_venta}'  where id='{id_venta}';"
        db.update_sql(sql)
        response = {"pieza": order_estados(get_estados_piezas(), nuevo_estado),
                    "producto": order_estados(get_estados_productos(), nuevo_estado_producto)["actual"],
                    "venta": order_estados(get_estados_ventas(), nuevo_estado_venta)["actual"]}
        return jsonify(response), 200
    return jsonify({"error": "No existe ese estado para la pieza"}), 500


def cancelar_venta(id_venta):
    id_estado_cancelar = get_id_estado_cancelado()
    # Cambiar estado venta
    sql = f"update ventas set idestado='{id_estado_cancelar}' " \
          f"where id='{id_venta}';"
    db.update_sql(sql)

    # Cambiar estado productos
    sql = f"update ventas_productos set idestado='{id_estado_cancelar}' " \
          f"where idventa='{id_venta}';"
    db.update_sql(sql)

    sql = f"update ventas_productos_piezas set idestado='{id_estado_cancelar}' " \
          f"where idproductoventa IN (select id from ventas_productos where idventa='{id_venta}');"
    db.update_sql(sql)


def cancelar_producto(id_producto):
    estado_cancelar = get_id_estado_cancelado()

    sql = f"update ventas_productos set idestado='{estado_cancelar}' " \
          f"where id='{id_producto}' RETURNING idventa;"
    id_venta = db.update_sql(sql, key='idventa')

    sql = f"update ventas_productos_piezas set idestado='{estado_cancelar}' " \
          f"where idproductoventa IN (select id from ventas_productos where id='{id_producto}');"
    db.update_sql(sql)

    sql = f"select avg(idestado) as estado from ventas_productos where idventa='{id_venta}';"
    if int(estado_cancelar) == int(db.select_first(sql)["estado"]):
        sql = f"update ventas set idestado='{estado_cancelar}' where id='{id_venta}'"
        db.update_sql(sql)


def entregar_venta(id_venta):
    sql = f"select id from estados where ventas='1' ORDER BY id DESC LIMIT 1 OFFSET 1"
    estado_entregado = db.select_first(sql)["id"]

    sql = f"update ventas set idestado='{estado_entregado}' where id='{id_venta}';"
    db.update_sql(sql)
