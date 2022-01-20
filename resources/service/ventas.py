import copy
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
            observaciones = str(p.get("observaciones", "")).split(',')

            for x in range(int(p["cantidad"])):
                try:
                    obs = observaciones[x]
                except:
                    obs = ""
                # Costo total
                costo_total = cotizacion.get_costo_total(id_producto)
                costo_total += extras.select_extras_by_id_product(id_producto)[1]

                # Precio unitario
                descuento = int(p.get("descuento", '0'))
                precio_unidad = round(
                    cotizacion.get_precio_unitario(id_producto)['preciounitario'] * (100 - descuento) / 100, 2)
                ganancia = round(precio_unidad - costo_total, 2)
                sql = f"INSERT INTO ventas_productos (idventa, idproducto, costototal, ganancia, descuento, " \
                      f"preciounidad, observaciones, adddata, idestado) " \
                      f"VALUES('{id_venta}','{id_producto}','{round(costo_total, 2)}','{ganancia}',{descuento}," \
                      f"{precio_unidad},'{obs}',''," \
                      f"(SELECT id FROM estados where productos='1' ORDER BY id ASC LIMIT 1 OFFSET 0)) " \
                      f"RETURNING id;"
                id_detalle = db.insert_sql(sql, key='id')

                sql = f"""INSERT INTO ventas_productos_piezas (idproductoventa, idpieza, idestado)
                (SELECT  '{id_detalle}', id, (SELECT id FROM estados where piezas='1' ORDER BY id ASC LIMIT 1 OFFSET 0) 
                FROM piezas WHERE idProducto = '{id_producto}')"""
                db.insert_sql(sql)

        return id_venta


def select_venta_by_id(_id):
    # Obtener venta
    sql = f"SELECT v.*, (SELECT COALESCE(SUM(pg.monto),0) FROM pagos pg WHERE pg.idventa = v.id) AS senia, " \
          f"(SELECT COALESCE(SUM(vp.preciounidad),0) FROM ventas_productos vp WHERE vp.idventa = v.id) AS preciototal " \
          f"FROM ventas AS v WHERE v.id= {_id};"
    venta = db.select_first(sql)
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
        return venta

    # Performance
    estados_productos = estados.get_estados_productos()
    estados_piezas = estados.get_estados_piezas()
    ids_products = list(str(x["idproducto"]) for x in productos)
    # sql = f"SELECT vpp.id as idpieza, vpp.idproductoventa, vpp.idestado, p.descripcion, p.horas, p.minutos " \
    #       f"FROM ventas_productos_piezas AS vpp " \
    #       f"INNER JOIN piezas AS p ON vpp.idpieza=p.id " \
    #       f"WHERE vpp.idproductoventa in ({','.join(ids_products)});"

    sql = f"select piezas.id as idpieza, * from piezas where idproducto in ({','.join(ids_products)});"
    piezas = db.select_multiple(sql)
    estado_listo = estados.get_id_estado_listo()

    for p in productos:
        # Obtener piezas
        # p["estado"] = estados.order_estados(copy.deepcopy(estados_productos), p["idestado"])
        p.pop("idestado", None)
        p.pop("idventa", None)
        p.pop("idproducto", None)

        p["piezas"] = [pi for pi in piezas if pi["idproducto"] == p["idproducto"]]
        # sum_piezas = 0
        # for pi in p["piezas"]:
        #     pi["estado"] = estados.order_estados(copy.deepcopy(estados_piezas), pi["idestado"])
        #     sum_piezas += 1 if pi["idestado"] == estado_listo else 0
        #     pi.pop("idestado", None)
        #
        # if sum_piezas != len(p['piezas']):
        #     p["descripcion"] += f" ({sum_piezas}/{len(p['piezas'])})"

    venta["productos"] = productos
    return venta


def get_all_ventas():
    estado_cancelado = estados.get_id_estado_cancelado()
    sql = f"SELECT v.*, e.estado, " \
          f" (SELECT count(vp.id) FROM ventas_productos vp WHERE " \
          f"vp.idventa = v.id and vp.idestado<>'{estados.get_id_estado_cancelado()}') AS productos, " \
          f" (SELECT sum(vp.preciounidad) FROM ventas_productos vp WHERE vp.idventa = v.id) AS precioTotal, " \
          f" (SELECT COALESCE(SUM(pg.monto),0) FROM pagos pg WHERE pg.idventa = v.id) AS senia " \
          f" FROM ventas AS v " \
          f" INNER JOIN estados AS e ON v.idestado = e.id " \
          f" WHERE idestado <>  '{estado_cancelado}'" \
          f" and (SELECT count(vp.id) FROM ventas_productos vp WHERE  vp.idventa = v.id and vp.idestado<>'{estado_cancelado}') > 0" \
          f" ORDER BY v.idestado DESC, senia DESC, productos DESC;"
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
