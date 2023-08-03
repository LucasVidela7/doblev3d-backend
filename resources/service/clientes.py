# decorator for verifying the JWT
import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from database import utils as db


def token_cliente_required(opcional=False):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if opcional:
                kwargs['user_id'] = None
            # jwt is passed in the request header
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            # return 401 if token is not passed
            if not token and not opcional:
                return jsonify({'message': 'Debe enviarse token'}), 403

            try:
                # decoding the payload to fetch the stored details
                data = jwt.decode(token, os.getenv('JWT_SECRET'))
                sql = f"SELECT id from clientes where id='{data['public_id']}';"
                user = db.select_first(sql)

                if not user:
                    raise Exception("Usuario no encontrado")

                kwargs['user_id'] = data['public_id']

            except jwt.ExpiredSignatureError:
                if not opcional:
                    return jsonify({
                        'message': 'Token expirado!'
                    }), 403
            except:
                if not opcional:
                    return jsonify({
                        'message': 'Token invalido!'
                    }), 403
            # returns the current logged in users contex to the routes
            return f(*args, **kwargs)

        return decorated

    return decorator


def login(auth):
    usuario = auth.get('usuario', False)
    password = auth.get('password', False)
    hash = auth.get('hash', False)

    if not auth or not usuario or not password or not hash:
        return jsonify({'message': 'No se están enviando todos los datos'}), 400

    if '@' in usuario:
        sql = f"SELECT * FROM clientes WHERE email='{usuario}';"
    else:
        sql = f"SELECT * FROM clientes WHERE dni='{usuario}';"
    user = db.select_first(sql)

    if not user:
        # returns 401 if user does not exist
        return jsonify({'message': 'Usuario y/o contraseña inválidos'}), 401

    if check_password_hash(user['password'], password):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user['id'],
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, os.getenv('JWT_SECRET'))

        sql = f"""UPDATE carrito SET idcliente='{user['id']}' WHERE hash='{hash}';"""
        db.update_sql(sql)
        return jsonify({'token': token.decode('UTF-8'), "expires_in": 30 * 60}), 200
    # returns 403 if password is wrong
    return jsonify({'message': 'Usuario y/o contraseña inválidos'}), 401


def registro(auth):
    dni = auth.get('dni', False)
    email = auth.get('email', False)
    password = auth.get('password', False)

    if not auth or not dni or not email or not password:
        # returns 401 if any email or / and password is missing
        return jsonify({'message': 'No se están enviando todos los datos'}), 400

    sql = f"SELECT * FROM clientes WHERE dni='{dni}' or email='{email}';"
    user = db.select_first(sql)

    if not user:
        # Crear usuario
        sql = f"INSERT INTO clientes (dni, password, email) " \
              f"VALUES ('{dni}','{generate_password_hash(password)}','{email}') RETURNING id;"
        id = db.insert_sql(sql, key='id')
        return jsonify({'message': 'Usuario registrado con éxito'}), 201
    else:
        return jsonify({'message': 'Ya hay una cuenta registrada con los datos ingresados'}), 417


def datos(user_id):
    sql = f"""SELECT dc.*, c.dni, c.email FROM datos_clientes as dc
            INNER JOIN clientes as c ON c.id = dc.id_cliente
            WHERE id_cliente='{user_id}';"""
    user = db.select_first(sql)
    return user


def guardar_datos(user_id, request):
    usuario = datos(user_id)

    if usuario:
        sql = f"DELETE FROM datos_clientes where id_cliente='{user_id}';"
        db.delete_sql(sql)

    keys = ["nombre", "apellido", "telefono", "domicilio", "numero", "depto", "piso",
            "entre_calles", "localidad", "codigo_postal", "principal"]

    cols = []
    vals = []

    for k, v in request.items():
        if k in keys:
            if v is None or v == '':
                continue
                # vals.append(f"null")
            else:
                cols.append(k)
                vals.append(f"'{v}'")

    sql = f"""INSERT INTO datos_clientes(id_cliente,{",".join(cols)})
            VALUES('{user_id}',{",".join(vals)}) RETURNING id;"""
    _ = db.insert_sql(sql, key='id')
    return True
