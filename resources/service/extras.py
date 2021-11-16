from database import utils as db


def get_all_extras():
    sql = f"SELECT * FROM extras"
    return db.select_multiple(sql)


def select_extras_by_id(id_product):
    sql = f"SELECT * FROM extra_producto WHERE idproducto= {id_product}"
    extras = list(db.select_multiple(sql))
    list_extras = []
    total_amount = 0
    for e in extras:
        sql = f"SELECT * FROM extras WHERE id= {e['idextra']}"
        ex = db.select_first(sql)
        list_extras.append(ex)
        total_amount += ex["precio"]
    return list_extras, round(total_amount, 2)


def add_extra(request):
    descripcion = request["desripcion"].upper()
    precio = request["precio"]
    sql = f"INSERT INTO extras(descripcion, precio) VALUES ('{descripcion}','{precio}') RETURNING id;"
    return db.insert_sql(sql, key='id')


def update_extra(_id, request):
    sql = f"UPDATE categorias SET categoria='{request['categoria'].upper()}' WHERE id='{_id}';"
    return db.update_sql(sql)
