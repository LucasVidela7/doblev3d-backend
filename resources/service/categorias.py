from database import utils as db


def get_all_categories():
    sql = f"SELECT * FROM categorias ORDER BY categoria ASC;"
    return db.select_multiple(sql)


def add_category(request):
    sql = f"INSERT INTO categorias(categoria) VALUES ('{request['categoria'].upper()}') RETURNING id;"
    return db.insert_sql(sql,key='id')


def update_category(_id, request):
    sql = f"UPDATE categorias SET categoria='{request['categoria'].upper()}' WHERE id='{_id}';"
    return db.update_sql(sql)
