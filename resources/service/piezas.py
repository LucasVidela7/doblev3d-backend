from database import utils as db


def select_piezas_by_id_product(_id):
    sql = f"SELECT descripcion, horas, minutos, peso FROM piezas WHERE idProducto= {_id}"
    return db.select_multiple(sql)
