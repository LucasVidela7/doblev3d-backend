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
    sql = f"SELECT *, cats.categoria AS categoria FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"WHERE p.id= {_id}"
    product = db.select_first(sql)
    # list_cat = categorias.get_all_categories()
    # list_cat = dict(map(lambda x: (x["id"], x), list_cat))
    # product["categoria"] = list_cat.get(product["idcategoria"], {}).get("categoria", "N/A")
    product["fechacreacion"] = product["fechacreacion"].strftime('%Y-%m-%d')
    return product


def get_all_products():

    sql = f"SELECT p.*, cats.categoria AS categoria, " \
          f"(SELECT * FROM precio_unitario WHERE idproducto=p.id ORDER BY id DESC) AS precioUnitario " \
          f"FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"ORDER BY p.estado DESC, p.id DESC;"
    # sql = f"SELECT * FROM productos ORDER BY estado DESC, id DESC;"
    products = [dict(p) for p in db.select_multiple(sql)]
    for p in products:
        p["fechacreacion"] = p["fechacreacion"].strftime('%Y-%m-%d')
        # p["precioUnitario"] = cotizacion.get_precio_unitario_by_product_id(p["id"])
        p["precioUnitarioVencido"] = cotizacion.get_precio_unitario_vencido(p["id"])
        p["ventas"] = cotizacion.get_ventas_by_product_id(p["id"])
    return products


def update_product(id_product, request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    estado = request['estado']

    sql = f"UPDATE productos SET descripcion='{descripcion}', idCategoria='{id_categoria}', estado='{estado}' where id={id_product}"
    db.update_sql(sql)
    sql = f"DELETE FROM piezas where idProducto={id_product}"
    db.delete_sql(sql)

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
