from database import utils as db


def get_all_categories_for_catalog():
    sql = f"SELECT * FROM categorias WHERE catalogo = true ORDER BY categoria ASC;"
    return db.select_multiple(sql)


def get_all_products_for_catalog(id_categoria):
    sql = f"SELECT p.id, p.descripcion, cats.categoria AS categoria, " \
          f"(SELECT count(id) FROM ventas_productos WHERE idproducto=p.id " \
          f"and idestado<>(SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 0)) AS ventas, " \
          f" (SELECT precioUnitario FROM precio_unitario WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as precioUnitario, " \
          f" (SELECT imagen FROM images WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as imagen " \
          f"FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"WHERE p.estado=true and p.idcategoria={id_categoria} " \
          f"ORDER BY precioUnitario DESC, ventas DESC;"
    products = [dict(p) for p in db.select_multiple(sql)]
    for p in products:
        p["fechacreacion"] = p["fechacreacion"].strftime('%Y-%m-%d')
    return products


def get_featured_products(limit=20):
    sql = f"SELECT p.id, p.descripcion, cats.categoria AS categoria, " \
          f"(SELECT count(id) FROM ventas_productos WHERE idproducto=p.id " \
          f"and idestado<>(SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 0)) AS ventas, " \
          f" (SELECT precioUnitario FROM precio_unitario WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as precioUnitario, " \
          f" (SELECT imagen FROM images WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as imagen " \
          f"FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"WHERE p.estado=true " \
          f"ORDER BY ventas DESC, precioUnitario DESC LIMIT {limit} OFFSET 0;"
    products = [dict(p) for p in db.select_multiple(sql) if p["ventas"] > 0]
    for p in products:
        p["fechacreacion"] = p["fechacreacion"].strftime('%Y-%m-%d')
    return products
