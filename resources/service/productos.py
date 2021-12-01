from datetime import datetime
from resources.service import categorias as categorias
from resources.service import cotizacion as cotizacion
from database import utils as db


def insert_product(request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')  # 2021-11-18

    sql = f"""INSERT INTO productos(descripcion,idCategoria, fechaCreacion)
            VALUES('{descripcion}','{id_categoria}','{fecha_creacion}') RETURNING id;"""
    id_product = db.insert_sql(sql, key='id')
    if id_product:
        for pieza in request.get("piezas", []):
            desc_piezas = pieza["descripcion"]
            peso_piezas = int(pieza["peso"])
            horas_piezas = int(pieza["horas"])
            minutos_piezas = int(pieza["minutos"])
            sql = f"""INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto)
                    VALUES('{desc_piezas}','{peso_piezas}','{horas_piezas}','{minutos_piezas}','{id_product}');
            """
            db.insert_sql(sql)
        for id_extra in request.get("extras", []):
            sql = f"""INSERT INTO extra_producto(idproducto, idextra)
                    VALUES('{id_product}','{id_extra}');"""
            db.insert_sql(sql)
        return id_product


def select_product_by_id(_id):
    sql = f"SELECT p.*, cats.categoria AS categoria FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"WHERE p.id= {_id}"
    product = db.select_first(sql)
    product["fechacreacion"] = product["fechacreacion"].strftime('%Y-%m-%d')
    return product


def get_all_products():
    sql = f"SELECT p.*, cats.categoria AS idcategoria, " \
          f"(SELECT count(id) FROM ventas_productos WHERE idproducto=p.id " \
          f"and idestado<>(SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 0)) AS ventas, " \
          f"(SELECT precioUnitario FROM precio_unitario WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as precioUnitario " \
          f"FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"ORDER BY p.estado DESC, p.id DESC;"
    products = [dict(p) for p in db.select_multiple(sql)]
    for p in products:
        p["fechacreacion"] = p["fechacreacion"].strftime('%Y-%m-%d')
        p["precioUnitarioVencido"] = cotizacion.get_precio_unitario_vencido(p["id"])
        p["precioUnitario"] = p["preciounitario"]
    return products


def update_product(id_product, request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    estado = request['estado']

    sql = f"UPDATE productos SET descripcion='{descripcion}', idCategoria='{id_categoria}', estado='{estado}' where id={id_product}"
    db.update_sql(sql)
    sql = f"UPDATE piezas SET idProducto = '0' where idProducto={id_product}"
    db.update_sql(sql)

    for pieza in request.get("piezas", []):
        desc_piezas = pieza["descripcion"]
        peso_piezas = int(pieza["peso"])
        horas_piezas = int(pieza["horas"])
        minutos_piezas = int(pieza["minutos"])
        sql = f"""INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto)
                VALUES('{desc_piezas}','{peso_piezas}','{horas_piezas}','{minutos_piezas}','{id_product}');"""
        db.insert_sql(sql)
    sql = f"DELETE FROM extra_producto where idProducto={id_product}"
    db.delete_sql(sql)

    for id_extra in request.get("extras", []):
        sql = f"""INSERT INTO extra_producto(idproducto, idextra)
                VALUES('{id_product}','{id_extra}');"""
        db.insert_sql(sql)
    return id_product
