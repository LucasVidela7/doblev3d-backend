import json
import pickle

from database import utils as db
from database.utils import redisx
from resources.service.productos import get_all_products


def get_all_categories_for_catalog():
    categorias = redisx.get('catalogo:categorias')
    if categorias is None:
        sql = f"SELECT * FROM categorias WHERE catalogo = true ORDER BY categoria ASC;"
        categorias = db.select_multiple(sql)
        redisx.set('catalogo:categorias', pickle.dumps(categorias))
    else:
        categorias = pickle.loads(categorias)
    return categorias


def get_all_products_for_catalog(id_categoria):
    products = get_all_products()
    categorias = dict(map(lambda x: (x["id"], x), get_all_categories_for_catalog()))
    products = [p for p in products if p['estado'] and p['idcategoria'] == categorias[id_categoria]["categoria"]]
    # sql = f"SELECT p.id, p.descripcion, cats.categoria AS categoria, " \
    #       f"(SELECT count(id) FROM ventas_productos WHERE idproducto=p.id " \
    #       f"and idestado<>(SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 0)) AS ventas, " \
    #       f" (SELECT precioUnitario FROM precio_unitario WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as precioUnitario, " \
    #       f" (SELECT imagen FROM images WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as imagen " \
    #       f"FROM productos AS p " \
    #       f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
    #       f"WHERE p.estado=true and p.idcategoria={id_categoria} " \
    #       f"ORDER BY precioUnitario DESC, ventas DESC;"
    # products = [dict(p) for p in db.select_multiple(sql)]
    return products[:20]


def get_featured_products(limit=20):
    products = get_all_products()
    products = [p for p in products if p['estado'] and p['idcategoria']]
    # sql = f"SELECT p.id, p.descripcion, cats.categoria AS categoria, " \
    #       f"(SELECT count(id) FROM ventas_productos WHERE idproducto=p.id " \
    #       f"and idestado<>(SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 0)) AS ventas, " \
    #       f" (SELECT precioUnitario FROM precio_unitario WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as precioUnitario, " \
    #       f" (SELECT imagen FROM images WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as imagen " \
    #       f"FROM productos AS p " \
    #       f"INNER JOIN categorias as cats ON cats.id = p.idcategoria and cats.catalogo=true " \
    #       f"WHERE p.estado=true " \
    #       f"ORDER BY ventas DESC, precioUnitario DESC LIMIT {limit} OFFSET 0;"
    # products = [dict(p) for p in db.select_multiple(sql)]  # if p["ventas"] > 0]
    return products[:limit]
