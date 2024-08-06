import json
import pickle

from database import utils as db

from database.utils import redisx


def get_all_extras():
    extras = redisx.get(f'extras')
    if extras is None:
        sql = f"SELECT * FROM extras"
        extras = db.select_multiple(sql)
        redisx.set(f'extras', pickle.dumps(extras))
    else:
        extras = pickle.loads(extras)
    return extras


def select_extras_by_id_product(id_product):
    extras = redisx.get(f'producto:{id_product}:extras')
    if extras is None:
        sql = f"""
                SELECT ex.* FROM extra_producto as ep
                INNER JOIN extras as ex ON ex.id = ep.idextra
                WHERE idproducto= {id_product}
                """
        extras = db.select_multiple(sql)
        redisx.set(f'producto:{id_product}:extras', pickle.dumps(extras))
    else:
        extras = pickle.loads(extras)
    total_amount = sum([ex["precio"] for ex in extras])
    return extras, round(total_amount, 2)


def get_products_by_extra_id(id_extra):
    sql = f"""
            SELECT p.id, p.descripcion FROM extra_producto as ep 
            INNER JOIN productos as p ON ep.idproducto = p.id
            WHERE idextra = '{id_extra}'
            """
    return db.select_multiple(sql)


def add_extra(request):
    descripcion = request["descripcion"].upper()
    precio = request["precio"]
    # categorias = request["categorias"]
    sql = f"INSERT INTO extras(descripcion, precio) VALUES ('{descripcion}','{precio}') RETURNING id;"
    id_extra = db.insert_sql(sql, key='id')

    # # Add extras to product id
    # sql = "INSERT INTO extra_categorias(idcategoria, idextra) VALUES "
    # sql += f",".join([f"('{c}', '{id_extra}')" for c in categorias])
    # sql += ";"
    # db.insert_sql(sql)
    redisx.delete('extras')
    return id_extra


def update_extra(_id, request):
    descripcion = request["descripcion"].upper()
    precio = request["precio"]
    # categorias = request["categorias"]

    sql = f"UPDATE extras SET descripcion='{descripcion}', precio='{precio}' WHERE id='{_id}';"
    db.update_sql(sql)

    # sql = f"DELETE FROM extra_categorias WHERE idextra='{_id}';"
    # db.delete_sql(sql)
    #
    # # Add extras to product id
    # sql = "INSERT INTO extra_categorias(idcategoria, idextra) VALUES "
    # sql += f",".join([f"('{c}', '{_id}')" for c in categorias])
    # sql += ";"
    # db.insert_sql(sql)
    redisx.delete('extras')
    try:
        redisx.delete(*redisx.keys('producto:*:extras'))
    except:
        return
    return


def select_extra_by_id(id_extra):
    sql = f"SELECT * FROM extras WHERE id='{id_extra}';"
    return db.select_first(sql)


def select_extra_by_id_categoria(id_categoria):
    all_extras = dict(map(lambda x: (x["id"], x), get_all_extras()))
    sql = f"SELECT idextra FROM extra_categorias where idcategoria='{id_categoria}';"
    ex_cats = db.select_multiple(sql)
    response = []
    for e in ex_cats:
        response.append(all_extras[e["idextra"]])

    return response


def delete_extra(id_extra):
    sql = f"DELETE FROM extra_categorias where idExtra='{id_extra}';"
    db.delete_sql(sql)
    sql = f"DELETE FROM extra_producto where idExtra='{id_extra}';"
    db.delete_sql(sql)
    sql = f"DELETE FROM extras where id='{id_extra}';"
    db.delete_sql(sql)
    redisx.delete('extras')
    try:
        redisx.delete(*redisx.keys('producto:*:extras'))
    except:
        return
    return
