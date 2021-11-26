from database import utils as db


def get_estados_ventas():
    sql = f"select id, estado, saltear from estados where ventas = '1';"
    return db.select_multiple(sql)


def get_estados_productos():
    sql = f"select id, estado, saltear from estados where productos = '1';"
    return db.select_multiple(sql)


def get_estados_piezas():
    sql = f"select id, estado, saltear from estados where piezas = '1';"
    return db.select_multiple(sql)


def order_estados(dictionary, actual_id_estado):
    # dictionary = dict(map(lambda x: (x["id"], x), dictionary))
    estados = {}
    for n, d in enumerate(dictionary):
        if d["id"] == actual_id_estado:
            estados["actual"] = d
            estados["actual"].pop("saltear")
            estados["siguientes"] = []
            estados["siguientes"].append(dictionary[n + 1])
            if dictionary[n + 1]["saltear"] == '1':
                estados["siguientes"].append(dictionary[n + 3])
                estados["siguientes"][0].pop("saltear")
                estados["siguientes"][1].pop("saltear")

            estados["anterior"] = {}
            if (n - 1) >= 0:
                estados["anterior"] = dictionary[n - 1]
                estados["anterior"].pop("saltear")

    return estados


def set_estados_venta(actual_id_estado):
    estados = get_estados_ventas()
    return order_estados(estados, actual_id_estado)
