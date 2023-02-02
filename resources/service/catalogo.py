import json
import pickle

from database import utils as db
from database.utils import redisx
from resources.service.categorias import get_all_categories
from resources.service.productos import get_all_products


def obtener_categorias_catalogo():
    # categorias = redisx.get('catalogo:categorias')
    # if categorias is None:
    #     sql = f"SELECT * FROM categorias WHERE catalogo = true ORDER BY categoria ASC;"
    #     categorias = db.select_multiple(sql)
    #     redisx.set('catalogo:categorias', pickle.dumps(categorias))
    # else:
    #     categorias = pickle.loads(categorias)
    categorias = get_all_categories()
    categorias = sorted([c for c in categorias if c['catalogo']], key=lambda d: d['categoria'])
    return categorias


def obtener_productos_por_categoria(id_categoria):
    products = get_all_products()
    categorias = dict(map(lambda x: (x["id"], x), obtener_categorias_catalogo()))
    products = [p for p in products if p['estado'] and p['categoria'] == categorias[id_categoria]["categoria"]]
    return products[:20]


def obtener_productos_destacados(limit=20):
    products = get_all_products()
    categorias = [c['categoria'] for c in obtener_categorias_catalogo()]
    products = [p for p in products if p['estado'] and p['categoria'] in categorias]
    return products[:limit]


def obtener_todos_productos(limit=20):
    return obtener_productos_destacados(limit=limit)
