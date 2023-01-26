import os
from datetime import datetime

from PIL.Image import Image
from flask import jsonify
from werkzeug.utils import secure_filename

from resources.service import cotizacion as cotizacion
from database import utils as db
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
                    peso = int(filament * 1000 / filament_kg)  # Regla de 3 simple para calcular peso

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
        return id_product


def select_product_by_id(_id):
    sql = f"SELECT p.*, cats.categoria AS categoria FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"WHERE p.id= {_id}"
    product = db.select_first(sql)

    product["fechacreacion"] = product["fechacreacion"].strftime('%Y-%m-%d')
    return product


def get_all_products():
    sql = f"SELECT p.*, cats.categoria AS idcategoria, " \
          f"(SELECT count(id) FROM ventas_productos WHERE idproducto=p.id " \
          f"and idestado<>(SELECT id FROM estados where productos='1' ORDER BY id DESC LIMIT 1 OFFSET 0)) AS ventas, " \
          f" (SELECT precioUnitario FROM precio_unitario WHERE idproducto=p.id ORDER BY id DESC LIMIT 1 OFFSET 0) as precioUnitario " \
          f"FROM productos AS p " \
          f"INNER JOIN categorias as cats ON cats.id = p.idcategoria " \
          f"ORDER BY p.estado DESC, precioUnitario DESC, ventas DESC;"
    products = [dict(p) for p in db.select_multiple(sql)]
    for p in products:
        p["fechacreacion"] = p["fechacreacion"].strftime('%Y-%m-%d')
        p["precioUnitarioVencido"] = cotizacion.get_precio_unitario_vencido(p["id"])
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
    return id_product


def delete_product(id_producto):
    if get_ventas_by_product_id(id_producto):
        return jsonify({"message": "No se puede borrar producto porque ventas"}), 406

    sql = f"delete from productos where id={id_producto}; " \
          f"delete from piezas where idproducto={id_producto};"
    db.delete_sql(sql)
    return jsonify({"message": "Producto borrado correctamente"}), 200


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ["jpg", "png", "jpeg"]  # ALLOWED_EXTENSIONS


def upload_image(files, id_producto):
    # check if the post request has the file part
    if 'file' not in files:
        return jsonify({"message": "Se debe enviar dentro de un key 'file'"}), 406
    file = files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({"message": "El archivo no tiene nombre"}), 406
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.getenv("FILE_STORE"), filename))
        sql = f"delete from images where id='{id_producto}';"
        db.delete_sql(sql)
        sql = f"INSERT INTO images(imagen,idproducto) VALUES('{filename}','{id_producto}');"
        db.insert_sql(sql)
        return jsonify({"message": "Imagen cargada correctamente"}), 200
    return jsonify({"message": "El archivo no cumple las extensiones adecuadas"}), 406
