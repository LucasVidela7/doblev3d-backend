from datetime import datetime
from resources.service import categorias as categorias
from resources.service import cotizacion as cotizacion
from database import utils as db


def insertar_venta(request):
    cliente = request['cliente']
    contacto = request['contacto']
    productos = request['productos']
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')  # 2021-11-18

    sql = f"""INSERT INTO ventas(cliente,fechaCreacion, contacto, idestado)
            VALUES('{cliente}','{fecha_creacion}','{contacto}',
            (SELECT id FROM estados ORDER BY id ASC LIMIT 1 OFFSET 0)) 
            RETURNING id;"""
    id_venta = db.insert_sql(sql, key='id')
    if id_venta:
        for p in productos:
            id_producto = p["id"]

            for x in range(int(p["cantidad"])):
                costo_total = float(p["costoTotal"])
                descuento = int(p["descuento"])
                monto_total = float(p["precioTotal"])
                ganancia = round(monto_total - costo_total, 2)
                observaciones = str(p.get("observaciones", ""))
                sql = f"INSERT INTO ventas_productos (idventa, idproducto, costototal, ganancia, descuento, " \
                      f"montototal, observaciones, adddata, idestado) " \
                      f"VALUES('{id_venta}','{id_producto}','{costo_total}','{ganancia}',{descuento}," \
                      f"{monto_total},'{observaciones}','',(SELECT id FROM estados ORDER BY id ASC LIMIT 1 OFFSET 0)) " \
                      f"RETURNING id;"
                id_detalle = db.insert_sql(sql, key='id')

                sql = f"""INSERT INTO ventas_productos_piezas (iddetalle, idpieza, idestado)
                (SELECT  '{id_detalle}', id, (SELECT id FROM estados ORDER BY id ASC LIMIT 1 OFFSET 0) 
                FROM piezas WHERE idProducto = '{id_producto}')"""
                print(sql)
                db.insert_sql(sql)

        return id_venta


def select_venta_by_id(_id):
    # Obtener venta
    sql = f"SELECT v.*, e.estado FROM ventas AS v " \
          f"INNER JOIN estados AS e ON v.idestado = e.id " \
          f"WHERE v.id= {_id};"
    venta = db.select_first(sql)
    venta["fechacreacion"] = venta["fechacreacion"].strftime('%Y-%m-%d')

    # Obtener productos
    sql = f"SELECT vp.*, p.descripcion FROM ventas_productos AS vp " \
          f"INNER JOIN productos AS p ON vp.idproducto=p.id " \
          f"WHERE idventa= {_id};"
    productos = db.select_multiple(sql)

    for p in productos:
        # Obtener piezas
        sql = f"SELECT vpp.idpieza, vpp.idestado, e.estado, p.descripcion " \
              f"FROM ventas_productos_piezas AS vpp " \
              f"INNER JOIN estados AS e ON vpp.idestado = e.id " \
              f"INNER JOIN piezas AS p ON vpp.idpieza=p.id " \
              f"WHERE vpp.iddetalle='{p['id']}';"
        p["piezas"] = db.select_multiple(sql)
        p.pop("idventa", None)

    venta["productos"] = productos
    return venta


def get_all_ventas():
    sql = f"SELECT v.*, e.estado, (SELECT count(vp.id) FROM ventas_productos vp WHERE vp.idventa = v.id) AS productos " \
          f"FROM ventas AS v " \
          f"INNER JOIN estados AS e ON v.idestado = e.id;"
    ventas = db.select_multiple(sql)
    for v in ventas:
        v["fechacreacion"] = v["fechacreacion"].strftime('%Y-%m-%d')
    return ventas
