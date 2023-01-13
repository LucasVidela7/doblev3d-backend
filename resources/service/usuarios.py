# decorator for verifying the JWT
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from database.connection import create_connection


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 403

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, "8ED81DD4F3589CF6A177DFD1B2D32")
            sql = f"SELECT id from usuarios where id='{data['public_id']}';"
            conn = create_connection()
            cur = conn.cursor()
            cur.execute(sql)
            if not cur.fetchone()[0]:
                raise Exception("Usuario no encontrado")

            # TODO Extender la sesión en cada consulta
        except:
            return jsonify({
                'message': 'Token is invalid !!'
            }), 403
        # returns the current logged in users contex to the routes
        return f(*args, **kwargs)

    return decorated


def login(auth):
    if not auth or not auth.get('usuario') or not auth.get('password'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    usuario = auth.get('usuario')
    password = auth.get('password')
    conn = create_connection()
    sql = f"SELECT * FROM usuarios WHERE usuario='{usuario}';"
    cur = conn.cursor()
    cur.execute(sql)
    user = cur.fetchone()

    if not user:
        # returns 401 if user does not exist
        return jsonify({'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}), 401

    if check_password_hash(user[2], password):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user[0],
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, "8ED81DD4F3589CF6A177DFD1B2D32")
        # TODO Agregar en un tabla "Sesiones" el tiempo de expiración, previamente buscar sesiones y borrarlas
        return jsonify({'token': token.decode('UTF-8'), "expires_in": 30 * 60}), 200
    # returns 403 if password is wrong
    return jsonify({'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}), 403

# # signup route
# @app.route('/signup', methods=['POST'])
# def signup():
#     # creates a dictionary of the form data
#     data = request.form
#
#     # gets name, email and password
#     name, email = data.get('name'), data.get('email')
#     password = data.get('password')
#
#     # checking for existing user
#     user = User.query \
#         .filter_by(email=email) \
#         .first()
#     if not user:
#         # database ORM object
#         user = User(
#             public_id=str(uuid.uuid4()),
#             name=name,
#             email=email,
#             password=generate_password_hash(password)
#         )
#         # insert user
#         db.session.add(user)
#         db.session.commit()
#
#         return make_response('Successfully registered.', 201)
#     else:
#         # returns 202 if user already exists
#         return make_response('User already exists. Please Log in.', 202)
