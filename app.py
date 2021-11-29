import pprint

from flask import Flask, request
from flask_cors import CORS
from flasgger import Swagger
from database.setup import create_tables
from resources.controller.extras import extras_bp
from resources.controller.productos import products_bp
from resources.controller.categorias import categorias_bp
from resources.controller.auth_usuarios import login_bp
from resources.controller.ventas import ventas_bp
from resources.controller.estados import estados_bp

app = Flask(__name__)
create_tables()
CORS(app)
Swagger(app)

app.register_blueprint(ventas_bp)
app.register_blueprint(estados_bp)
app.register_blueprint(products_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(extras_bp)
app.register_blueprint(login_bp)

app.config['SECRET_KEY'] = '8ED81DD4F3589CF6A177DFD1B2D32'


@app.before_request
def log_request_info():
    print('Headers: %s \n Method: %s\n Request: \n%s',
                    request.headers, request.method,
                    pprint.pformat(request.json, indent=4))


@app.after_request
def log_response_info(response):
    print('Response: \n%s', pprint.pformat(response.json, indent=4))
    return response


if __name__ == '__main__':
    app.run(debug=True)
