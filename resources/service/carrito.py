from database import utils as db


def vaciar_carrito():
    sql = "DELETE FROM carrito WHERE time < now()-'3 hours'::interval;"
    db.delete_sql(sql)


def obtener_carrito(hash):
    vaciar_carrito()
    sql = f"""
    SELECT 
    c.hash,
    c.idproducto,
    SUM(c.cantidad) as cantidad,
    p.descripcion,
    img.imagen,	
    pu.preciounitario
    FROM carrito as c
    INNER JOIN productos as p ON p.id = c.idproducto 
    LEFT OUTER JOIN images as img ON img.idproducto = c.idproducto
    LEFT OUTER JOIN precio_unitario as pu ON pu.idproducto = c.idproducto
    WHERE hash = '{hash}'
    GROUP BY
    c.idproducto,
    c.hash,
    p.descripcion,
    img.imagen,	
    pu.preciounitario
    """
    carrito = db.select_multiple(sql)
    return carrito


def agregar_carrito(request):
    hash = request.get('hash', False)
    id_producto = request.get('idProducto', False)
    cantidad = request.get('cantidad', 1)

    if not hash or not id_producto:
        return False

    sql = f""" DELETE FROM carrito WHERE hash='{hash}' and idproducto={id_producto};"""
    db.delete_sql(sql)

    sql = f"""INSERT INTO carrito (hash, idproducto, cantidad) 
        VALUES('{hash}',{id_producto},{cantidad})"""
    db.insert_sql(sql)

    sql = f"UPDATE carrito SET time = now() where hash = '{hash}';"
    db.update_sql(sql)

    return True


def borrar_carrito(hash, id_producto):
    if not hash or not id_producto:
        return False

    sql = f"""DELETE FROM carrito where hash='{hash}' and idproducto={id_producto}"""
    db.delete_sql(sql)
    return True
