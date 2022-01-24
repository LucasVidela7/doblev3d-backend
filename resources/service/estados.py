from functools import lru_cache

from flask import jsonify

from database import utils as db


def get_estados_ventas():
    sql = f"select id, estado, saltear, icono from estados where ventas = '1';"
    return db.select_multiple(sql)


def get_estados_productos():
    sql = f"select id, estado, saltear, icono from estados where productos = '1';"
    return db.select_multiple(sql)


def get_id_estado_cancelado():
    sql = "SELECT id FROM estados ORDER BY id DESC LIMIT 1;"
    return db.select_first(sql)["id"]


def get_id_estado_listo():
    sql = "SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 1;"
    return db.select_first(sql)["id"]


def order_estados(dictionary, actual_id_estado):
    # dictionary = dict(map(lambda x: (x["id"], x), dictionary))
    estados = {}
    for n, d in enumerate(dictionary):
        if d["id"] == actual_id_estado:
            estados["actual"] = d
            estados["actual"].pop("saltear")
            estados["siguientes"] = []
            estados["anterior"] = []

            if (n - 1) >= 0:
                estados["anterior"].append(dictionary[n - 1].pop("saltear"))

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


def cambiar_estado_producto(request):
    id_producto = request["idProducto"]  # Pieza asociada al producto de la venta
    nuevo_estado = request["idEstado"]

    list_estados_ventas = get_estados_ventas()
    list_estados_productos = get_estados_productos()

    estados_ventas = [v["id"] for v in list_estados_ventas]
    estados_productos = [p["id"] for p in list_estados_productos]

    if nuevo_estado in estados_productos:

        # Cambiar estado pieza
        sql = f"update ventas_productos set idestado='{nuevo_estado}' where id='{id_producto}' RETURNING idventa;"
        id_venta = db.update_sql(sql, key='idventa')

        # Verificar estado venta
        sql = f"select AVG(idestado) as estados_productos from ventas_productos where idventa='{id_venta}';"
        nuevo_estado_venta = int(db.select_first(sql)["estados_productos"])
        if nuevo_estado_venta not in estados_ventas:
            for n, ev in enumerate(estados_ventas):
                if ev < nuevo_estado_venta and n > 0:
                    nuevo_estado_venta = ev
                    break

        # Cambiar estado venta
        sql = f"update ventas set idestado='{nuevo_estado_venta}'  where id='{id_venta}';"
        db.update_sql(sql)
        response = {"producto": order_estados(list_estados_productos, nuevo_estado),
                    "venta": order_estados(list_estados_ventas, nuevo_estado_venta)["actual"]}
        return jsonify(response), 200
    return jsonify({"error": "No existe ese estado para la pieza"}), 500


def cancelar_venta(id_venta):
    # Cambiar estado productos
    sql = f"delete from ventas where id='{id_venta}';" \
          f"delete from ventas_productos where idventa='{id_venta}';"
    db.update_sql(sql)


def cancelar_producto(id_producto):
    estado_cancelar = get_id_estado_cancelado()
    sql = f"select avg(idestado) as estado, " \
          f"(select idventa from ventas_productos where id='{id_producto}') as idventa " \
          f"from ventas_productos " \
          f"where idventa=(select idventa from ventas_productos where id='{id_producto}') and id<>'{id_producto}';"
    consult = db.select_first(sql)
    if int(estado_cancelar) == int(consult["estado"]):
        cancelar_venta(consult["idventa"])
    else:
        sql = f"update ventas_productos set idestado='{estado_cancelar}', preciounidad='0' " \
              f"where id='{id_producto}'"
        db.update_sql(sql)

    return jsonify({"mensaje": "Cancelado con exito"}), 200


def entregar_venta(id_venta):
    sql = f"select id from estados where ventas='1' ORDER BY id DESC LIMIT 1 OFFSET 1"
    estado_entregado = db.select_first(sql)["id"]

    sql = f"update ventas set idestado='{estado_entregado}' where id='{id_venta}';"
    db.update_sql(sql)

    # Cambiar estado productos
    sql = f"update ventas_productos set idestado='{get_id_estado_listo()}' " \
          f"where idventa='{id_venta}' and idestado <> '{get_id_estado_cancelado()}';"
    db.update_sql(sql)
