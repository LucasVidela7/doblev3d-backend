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


def order_estados(dictionary, actual_id_estado):
    # dictionary = dict(map(lambda x: (x["id"], x), dictionary))
    estados = {}
    for n, d in enumerate(dictionary):
        if d["id"] == actual_id_estado:
            estados["actual"] = d
            estados["actual"].pop("saltear")
            estados["siguientes"] = []
            estados["siguientes"].append(dictionary[n + 1])
            if dictionary[n + 1]["saltear"] == '1':
                estados["siguientes"].append(dictionary[n + 3])
                estados["siguientes"][0].pop("saltear")
                estados["siguientes"][1].pop("saltear")

            estados["anterior"] = {}
            if (n - 1) >= 0:
                estados["anterior"] = dictionary[n - 1]
                estados["anterior"].pop("saltear")

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
        nuevo_estado_producto = db.select_first(sql)["estados_piezas"]
        if nuevo_estado_producto not in estados_productos:
            for n, ep in enumerate(estados_productos):
                if ep > nuevo_estado_producto and n > 0:
                    nuevo_estado_producto = ep
                    break

        # Cambiar estado producto
        sql = f"update ventas_productos set idestado='{nuevo_estado_producto}' " \
              f"where id='{id_producto_venta}' RETURNING idventa;"
        id_venta = db.update_sql(sql, key='idventa')

        # Verificar estado venta
        sql = f"select max(idestado) as estados_productos from ventas_productos " \
              f"where idventa='{id_venta}';"
        nuevo_estado_venta = db.select_first(sql)["estados_productos"]
        if nuevo_estado_venta not in estados_ventas:
            for n, ev in enumerate(estados_ventas):
                if ev < nuevo_estado_venta and n > 0:
                    nuevo_estado_venta = ev
                    break

        # Cambiar estado venta
        sql = f"update ventas set idestado='{nuevo_estado_venta}'  where id='{id_venta}';"
        db.update_sql(sql)
