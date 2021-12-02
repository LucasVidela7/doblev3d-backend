from datetime import datetime
from resources.service import extras as extras
from resources.service import cotizacion as cotizacion
from resources.service import estados as estados
from database import utils as db


def insertar_venta(request):
    cliente = request['cliente']
    contacto = request['contacto']
    productos = request['productos']
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')  # 2021-11-18

    sql = f"""INSERT INTO ventas(cliente,fechaCreacion, contacto, idestado)
            VALUES('{cliente}','{fecha_creacion}','{contacto}',
            (SELECT id FROM estados where ventas='1' ORDER BY id ASC LIMIT 1 OFFSET 0)) 
            RETURNING id;"""
    id_venta = db.insert_sql(sql, key='id')
    if id_venta:
        for p in productos:
            id_producto = p["id"]

            for x in range(int(p["cantidad"])):
                # Costo total
                costo_total = cotizacion.get_costo_total(id_producto)
                costo_total += extras.select_extras_by_id_product(id_producto)[1]

                # Precio unitario
                descuento = int(p.get("descuento", '0'))
                precio_unidad = round(
                    cotizacion.get_precio_unitario(id_producto)['preciounitario'] * (100 - descuento) / 100, 2)
                ganancia = round(precio_unidad - costo_total, 2)
                observaciones = str(p.get("observaciones", ""))
                sql = f"INSERT INTO ventas_productos (idventa, idproducto, costototal, ganancia, descuento, " \
                      f"preciounidad, observaciones, adddata, idestado) " \
                      f"VALUES('{id_venta}','{id_producto}','{round(costo_total, 2)}','{ganancia}',{descuento}," \
                      f"{precio_unidad},'{observaciones}',''," \
                      f"(SELECT id FROM estados where productos='1' ORDER BY id ASC LIMIT 1 OFFSET 0)) " \
                      f"RETURNING id;"
                id_detalle = db.insert_sql(sql, key='id')

                sql = f"""INSERT INTO ventas_productos_piezas (idproductoventa, idpieza, idestado)
                (SELECT  '{id_detalle}', id, (SELECT id FROM estados where piezas='1' ORDER BY id ASC LIMIT 1 OFFSET 0) 
                FROM piezas WHERE idProducto = '{id_producto}')"""
                print(sql)
                db.insert_sql(sql)

        return id_venta


def select_venta_by_id(_id):
    # Obtener venta
    sql = f"SELECT v.*, (SELECT COALESCE(SUM(pg.monto),0) FROM pagos pg WHERE pg.idventa = v.id) AS senia " \
          f"FROM ventas AS v WHERE v.id= {_id};"
    venta = db.select_first(sql)
    venta["fechacreacion"] = venta["fechacreacion"].strftime('%Y-%m-%d')
    venta["estado"] = estados.order_estados(estados.get_estados_ventas(), venta["idestado"])
    venta.pop("idestado", None)

    # Obtener productos
    sql = f"SELECT vp.*, p.descripcion FROM ventas_productos AS vp " \
          f"INNER JOIN productos AS p ON vp.idproducto=p.id " \
          f"WHERE idventa= {_id};"
    productos = db.select_multiple(sql)

    for p in productos:
        # Obtener piezas
        p["estado"] = estados.order_estados(estados.get_estados_productos(), p["idestado"])
        p.pop("idestado", None)
        sql = f"SELECT vpp.id as idpieza, vpp.idestado, p.descripcion, p.horas, p.minutos " \
              f"FROM ventas_productos_piezas AS vpp " \
              f"INNER JOIN piezas AS p ON vpp.idpieza=p.id " \
              f"WHERE vpp.idproductoventa='{p['id']}';"
        p["piezas"] = db.select_multiple(sql)
        p.pop("idventa", None)
        for pi in p["piezas"]:
            pi["estado"] = estados.order_estados(estados.get_estados_piezas(), pi["idestado"])
            pi.pop("idestado", None)

    venta["productos"] = productos
    return venta


def get_all_ventas():
    sql = f"SELECT v.*, e.estado, " \
          f" (SELECT count(vp.id) FROM ventas_productos vp WHERE vp.idventa = v.id) AS productos, " \
          f" (SELECT sum(vp.preciounidad) FROM ventas_productos vp WHERE vp.idventa = v.id) AS precioTotal, " \
          f" (SELECT COALESCE(SUM(pg.monto),0) FROM pagos pg WHERE pg.idventa = v.id) AS senia " \
          f" FROM ventas AS v " \
          f" INNER JOIN estados AS e ON v.idestado = e.id " \
          f" WHERE idestado <> (SELECT id FROM estados ORDER BY id DESC LIMIT 1) " \
          f" ORDER BY v.idestado DESC, senia DESC, productos DESC;"
    ventas = db.select_multiple(sql)
    for v in ventas:
        v["fechacreacion"] = v["fechacreacion"].strftime('%Y-%m-%d')

    return ventas
