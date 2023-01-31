import pickle

from flask import jsonify

from database import utils as db
from database.utils import redisx


def get_all_categories():
    categorias = redisx.get('categorias')
    if categorias is None:
        sql = f"SELECT *, categoria AS descripcion, " \
              f"(SELECT count(p.idcategoria) FROM productos p WHERE p.idcategoria = categorias.id) AS productos " \
              f"FROM categorias ORDER BY categoria ASC;"
        categorias = db.select_multiple(sql)
        redisx.set('categorias', pickle.dumps(categorias))
    else:
        categorias = pickle.loads(categorias)
    return categorias


def add_category(request):
    categoria = request['categoria'].upper()
    catalogo = request.get('catalogo', True)
    margen = request.get('margen', 50)
    sql = f"INSERT INTO categorias(categoria, catalogo, margen) " \
          f"VALUES ('{categoria}','{catalogo}', '{margen}') RETURNING id;"

    redisx.delete('categorias')
    redisx.delete('catalogo:categorias')
    return db.insert_sql(sql, key='id')


def update_category(_id, request):
    categoria = request['categoria'].upper()
    catalogo = request['catalogo']
    margen = request['margen']
    sql = f"UPDATE categorias SET categoria='{categoria}', catalogo='{catalogo}', margen='{margen}' WHERE id='{_id}';"
    redisx.delete('categorias')
    redisx.delete('catalogo:categorias')
    return db.update_sql(sql)


def get_categories_by_extras(id_extra):
    all_cats = get_all_categories()
    sql = f"SELECT idCategoria FROM extra_categorias WHERE idExtra='{id_extra}';"
    exs_cats = dict(map(lambda x: (x["idcategoria"], x), db.select_multiple(sql)))

    for cat in all_cats:
        cat["check"] = bool(exs_cats.get(cat["id"], False))

    return all_cats


def delete_category(id_categoria):
    sql = f"select * from productos where idcategoria={id_categoria}"
    cats = db.select_multiple(sql)

    if cats:
        return jsonify({"message": "La categoria tiene productos asignados"}), 406

    sql = f"DELETE FROM extra_categorias WHERE idcategoria='{id_categoria}';" \
          f"DELETE FROM categorias WHERE id='{id_categoria}';"
    db.delete_sql(sql)

    redisx.delete('categorias')
    redisx.delete('catalogo:categorias')

    return jsonify({"message": "Categoria borrada con exito"}), 200
