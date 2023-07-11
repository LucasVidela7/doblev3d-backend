import json

from resources.service.categorias import get_all_categories
from resources.service.productos import get_all_products
import resources.service.ofertas as ofertas


def set_ofertas(productos):
    ofertass = ofertas.get_ofertas_vigentes()

    ofs = [o for o in ofertass if o['tipo'] == 'TIENDA']
    if ofs:
        for p in productos:
            p['porcentaje'] = int(ofs[0]['porcentaje'])
            p['precioOferta'] = p['preciounitario'] * (100 - ofs[0]['porcentaje']) / 100
        return productos

    ofs_categoria = [o for o in ofertass if o['tipo'] == 'CATEGORIA']
    for c in ofs_categoria:
        c.update(json.loads(c['objeto']))
        c.pop('objeto', None)

    ofs_categoria = dict(map(lambda x: (x["id_categoria"], x), ofs_categoria))

    for p in productos:
        of = ofs_categoria.get(str(p['idcategoria']), False)
        if of:
            p['porcentaje'] = int(of['porcentaje'])
            p['precioOferta'] = p['preciounitario'] * (100 - of['porcentaje']) / 100


def obtener_categorias_catalogo():
    categorias = get_all_categories()
    categorias = sorted([c for c in categorias if c['catalogo']], key=lambda d: d['categoria'])
    return categorias


def obtener_productos_por_categoria(id_categoria):
    products = get_all_products()
    categorias = dict(map(lambda x: (x["id"], x), obtener_categorias_catalogo()))
    products = [p for p in products if p['estado'] and p['categoria'] == categorias[id_categoria]["categoria"]]
    set_ofertas(products)
    return products


def obtener_productos_destacados(limit=20):
    products = get_all_products()
    categorias = [c['categoria'] for c in obtener_categorias_catalogo()]
    # products = [p for p in products if p['estado'] and p['categoria'] in categorias]
    products = [p for p in products if p['estado'] and p['categoria'] in categorias and p['imagen'] is not None]
    set_ofertas(products)
    return products[:limit]


def obtener_producto_catalogo(id):
    products = get_all_products()
    productos = [p for p in products if p["id"] == id]
    set_ofertas(productos)
    return productos[0]


def obtener_todos_productos(limit=20):
    return obtener_productos_destacados(limit=limit)
