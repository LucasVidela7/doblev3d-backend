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
    products = [p for p in products if p['estado'] and p['categoria'] == categorias[id_categoria]["categoria"]]
    return products[:20]


def get_featured_products(limit=20):
    products = get_all_products()
    categorias = [c['categoria'] for c in get_all_categories_for_catalog()]
    products = [p for p in products if p['estado'] and p['categoria'] in categorias]
    return products[:limit]
