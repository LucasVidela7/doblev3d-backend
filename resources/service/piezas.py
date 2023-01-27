import pickle

from database import utils as db
from database.utils import redisx


def select_piezas_by_id_product(_id):
    piezas = redisx.get(f'productos:{_id}:piezas')

    if piezas is None:
        sql = f"SELECT descripcion, horas, minutos, peso FROM piezas WHERE idProducto= {_id}"
        piezas = db.select_multiple(sql)
        redisx.set(f'productos:{_id}:piezas', pickle.dumps(piezas))
    else:
        piezas = pickle.loads(piezas)

    return piezas
