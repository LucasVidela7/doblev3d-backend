import os
import pickle
from datetime import datetime
from flask import jsonify
from werkzeug.utils import secure_filename

from database.tinify import Tinify
from database.utils import redisx
from database import utils as db
from resources.service.cotizacion import prices_db, insert_precio_unitario
from resources.service.ventas import get_ventas_by_product_id


def insert_product(request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    fecha_creacion = datetime.now().strftime('%Y-%m-%d')  # 2021-11-18

    sql = f"""INSERT INTO productos(descripcion,idCategoria, fechaCreacion)
            VALUES('{descripcion}','{id_categoria}','{fecha_creacion}') RETURNING id;"""
    id_product = db.insert_sql(sql, key='id')

    if id_product:
        piezas = request.get("piezas", [])
        drag_and_drop = request.get("dragAndDrop", [])
        if drag_and_drop:
            for p in drag_and_drop:
                for descripcion, values in p.items():
                    time = int(values["time"])
                    filament = float(values["filament_used"])
                    filament_kg = 300  # 1kg filamento TODO Setear por base
                    peso = int(filament * 1000 / filament_kg) + 1  # Regla de 3 simple para calcular peso

                    minutes, seconds = divmod(time, 60)
                    hours, minutes = divmod(minutes, 60)
                    piezas.append({"descripcion": descripcion, "peso": peso, "horas": hours, "minutos": minutes})

        if piezas:
            sql = "INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto) VALUES "
            sql += f",".join(
                [
                    f"('{p['descripcion']}', '{int(p['peso'])}', '{int(p['horas'])}', '{int(p['minutos'])}', '{id_product}')"
                    for p in piezas])
            sql += ";"
            db.insert_sql(sql)

        extras = request.get("extras", [])
        if extras:
            sql = "INSERT INTO extra_producto(idproducto, idextra) VALUES "
            sql += f",".join([f"('{id_product}', '{id_extra}')" for id_extra in extras])
            sql += ";"
            db.insert_sql(sql)

        insert_precio_unitario(id_product, 0)
        redisx.delete(f"productos")
        return id_product


def select_product_by_id(_id):
    product = redisx.get(f'producto:{_id}:detalle')
    if product is None:
        sql = f"SELECT p.*, cats.categoria AS categoria FROM productos AS p " \
              f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
              f"WHERE p.id= {_id}"
        product = db.select_first(sql)
        redisx.set(f'producto:{_id}:detalle', pickle.dumps(product))
    else:
        product = pickle.loads(product)

    product["fechacreacion"] = product["fechacreacion"].strftime('%Y-%m-%d')
    return product


def get_all_products():
    products = redisx.get('productos')

    if products is None:
        sql = f"""
        SELECT p.*, cats.id AS idcategoria, cats.categoria AS categoria, 
        (SELECT count(id) FROM ventas_productos WHERE idproducto=p.id and 
        idestado<>(SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 0)) AS ventas,  
        pu.precioUnitario as precioUnitario,
        CAST(CASE WHEN pu.fechaActualizacion + {int(prices_db()['diasVencimiento'])} < CURRENT_DATE THEN true ELSE false END AS boolean) AS precioUnitarioVencido,
        (SELECT imagen FROM images WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as imagen 
        FROM productos AS p 
        INNER JOIN categorias as cats ON cats.id = p.idcategoria 
        INNER JOIN precio_unitario as pu ON idproducto=p.id 
        ORDER BY p.estado DESC, precioUnitario DESC, ventas DESC;
        """
        products = db.select_multiple(sql)
        redisx.set('productos', pickle.dumps(products))
    else:
        products = pickle.loads(products)
    products = [dict(p) for p in products]
    for p in products:
        p["fechacreacion"] = p["fechacreacion"].strftime('%Y-%m-%d')
        p["precioUnitarioVencido"] = p.get("preciounitariovencido", True)
        p.pop("preciounitariovencido", None)
    return products


def update_product(id_product, request):
    descripcion = request['descripcion']
    id_categoria = request['idCategoria']
    estado = request['estado']

    sql = f"UPDATE productos SET descripcion='{descripcion}', idCategoria='{id_categoria}', estado='{estado}' " \
          f"where id={id_product}"
    db.update_sql(sql)

    sql = f"delete from piezas where idProducto={id_product}"
    db.delete_sql(sql)

    piezas = request.get("piezas", [])
    if piezas:
        sql = "INSERT INTO piezas(descripcion, peso, horas, minutos, idProducto) VALUES "
        sql += f",".join(
            [f"('{p['descripcion']}', '{int(p['peso'])}', '{int(p['horas'])}', '{int(p['minutos'])}', '{id_product}')"
             for p in piezas])
        sql += ";"
        db.insert_sql(sql)

    sql = f"DELETE FROM extra_producto where idProducto={id_product}"
    db.delete_sql(sql)

    extras = request.get("extras", [])
    if extras:
        sql = "INSERT INTO extra_producto(idproducto, idextra) VALUES "
        sql += f",".join([f"('{id_product}', '{id_extra}')" for id_extra in extras])
        sql += ";"
        db.insert_sql(sql)

    redisx.delete(*redisx.keys(f"producto:{id_product}:*"))
    redisx.delete(f"productos")
    return id_product


def delete_product(id_producto):
    if get_ventas_by_product_id(id_producto):
        return jsonify({"message": "No se puede borrar producto porque ventas"}), 406

    sql = f"delete from productos where id={id_producto}; " \
          f"delete from piezas where idproducto={id_producto};"
    db.delete_sql(sql)

    redisx.delete(*redisx.keys(f"producto:{id_producto}:*"))
    redisx.delete(f"productos")
    return jsonify({"message": "Producto borrado correctamente"}), 200


def upload_image(files, id_producto):
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ["jpg", "png", "jpeg"]  # ALLOWED_EXTENSIONS

    def formalize_filename(filename, id_producto):
        name = filename.split(".")
        return f"producto_{id_producto}.{name[1]}"

    # check if the post request has the file part
    if 'file' not in files:
        return jsonify({"message": "Se debe enviar dentro de un key 'file'"}), 406
    file = files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"message": "El archivo no tiene nombre"}), 406
    if file and allowed_file(file.filename):
        filename = secure_filename(formalize_filename(file.filename, id_producto))
        file.save(os.path.join(os.getenv("FILE_STORE"), filename))
        sql = f"delete from images where idproducto='{id_producto}';"
        db.delete_sql(sql)
        sql = f"INSERT INTO images(imagen,idproducto) VALUES('https://doblev3d.mooo.com/images/{filename}','{id_producto}');"
        db.insert_sql(sql)
        redisx.delete(f"productos")
        return jsonify({"message": "Imagen cargada correctamente"}), 200
    return jsonify({"message": "El archivo no cumple las extensiones adecuadas"}), 406


def resize_image():
    sql = "SELECT * from images WHERE imagen NOT LIKE '%.webp';"
    imagenes = db.select_multiple(sql)
    tinify = Tinify()
    for img in imagenes:
        response = tinify.post_image(img['imagen'])
        if response.status_code == 201:
            a = tinify.get_image(response.json()['output']['url'])
            filename = img['imagen'].split('/')[-1].split('.')[0]
            with open(f"{os.getenv('FILE_STORE')}/{filename}.webp", "wb") as file:
                file.write(a.content)
            sql = f"""UPDATE images SET imagen='{filename}' WHERE imagen='{img['imagen']}';"""
            db.update_sql(sql)
            print(f"{os.getenv('FILE_STORE')}/{img['imagen'].split['/'][-1]}")
            os.remove(f"{os.getenv('FILE_STORE')}/{img['imagen'].split('/')[-1]}")
            print(f"{img['imagen']}: Exito")
        else:
            print(f"{img['imagen']}: Falló")
    return imagenes
