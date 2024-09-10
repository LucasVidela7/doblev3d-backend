from database import utils as db
from resources.service.catalogo import set_ofertas


def vaciar_carrito():
    sql = "DELETE FROM carrito WHERE time < now()-'3 hours'::interval;"
    db.delete_sql(sql)


def obtener_carrito_by_hash(hash):
    vaciar_carrito()
    sql = f"""
    SELECT 
    c.idproducto,
    SUM(c.cantidad) as cantidad,
    p.descripcion,
	p.idcategoria,
    img.imagen,	
    pu.preciounitario
    FROM carrito as c
    INNER JOIN productos as p ON p.id = c.idproducto 
    LEFT OUTER JOIN images as img ON img.idproducto = c.idproducto
    LEFT OUTER JOIN precio_unitario as pu ON pu.idproducto = c.idproducto
    WHERE hash = '{hash}'
    GROUP BY
    c.idproducto,
    p.descripcion,
	p.idcategoria,
    img.imagen,	
    pu.preciounitario
    """
    carrito = db.select_multiple(sql)
    set_ofertas(carrito)
    return carrito


def obtener_carrito_by_user_id(user_id):
    vaciar_carrito()
    sql = f"""
    SELECT 
    c.idproducto,
    SUM(c.cantidad) as cantidad,
    p.descripcion,
	p.idcategoria,
    img.imagen,	
    pu.preciounitario
    FROM carrito as c
    INNER JOIN productos as p ON p.id = c.idproducto 
    LEFT OUTER JOIN images as img ON img.idproducto = c.idproducto
    LEFT OUTER JOIN precio_unitario as pu ON pu.idproducto = c.idproducto
    WHERE idcliente = '{user_id}'
    GROUP BY
    c.idproducto,
    p.descripcion,
	p.idcategoria,
    img.imagen,	
    pu.preciounitario
    """
    carrito = db.select_multiple(sql)
    set_ofertas(carrito)
    return carrito


def agregar_carrito(id_producto, cantidad, hash=None, user_id=None):
    if hash:
        sql = f""" DELETE FROM carrito WHERE hash='{hash}' and idproducto={id_producto};"""
        db.delete_sql(sql)
        sql = f"""INSERT INTO carrito (hash, idproducto, cantidad) 
            VALUES('{hash}',{id_producto},{cantidad})"""
        db.insert_sql(sql)
        sql = f"UPDATE carrito SET time = now() where hash = '{hash}';"
        db.update_sql(sql)
    elif user_id:
        sql = f""" DELETE FROM carrito WHERE idcliente='{user_id}' and idproducto={id_producto};"""
        db.delete_sql(sql)
        sql = f"""INSERT INTO carrito (idcliente, idproducto, cantidad) 
            VALUES('{user_id}',{id_producto},{cantidad})"""
        db.insert_sql(sql)
        sql = f"UPDATE carrito SET time = now() where idcliente='{user_id}';"
        db.update_sql(sql)
    return True


def borrar_carrito(id_producto, hash=None, user_id=None):
    if hash:
        sql = f"""DELETE FROM carrito where hash='{hash}' and idproducto={id_producto}"""
        db.delete_sql(sql)
    elif user_id:
        sql = f"""DELETE FROM carrito where idcliente='{user_id}' and idproducto={id_producto}"""
        db.delete_sql(sql)
    return True
