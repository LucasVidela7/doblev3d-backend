from flask import jsonify

from database import utils as db


def get_all_categories():
    sql = f"SELECT *, (SELECT count(p.idcategoria) FROM productos p WHERE p.idcategoria = categorias.id) AS productos" \
          f" FROM categorias ORDER BY categoria ASC;"
    return db.select_multiple(sql)


def add_category(request):
    sql = f"INSERT INTO categorias(categoria) VALUES ('{request['categoria'].upper()}') RETURNING id;"
    return db.insert_sql(sql, key='id')


def update_category(_id, request):
    sql = f"UPDATE categorias SET categoria='{request['categoria'].upper()}' WHERE id='{_id}';"
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

    return jsonify({"message": "Categoria borrada con exito"}), 200
