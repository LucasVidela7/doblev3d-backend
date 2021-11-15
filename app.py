import json
import pprint

from flask import Flask, request
from flask_cors import CORS
from flasgger import Swagger
from database.setup import create_tables
from resources.controller.extras import extras_bp
from resources.controller.products import products_bp
from resources.controller.categorias import categorias_bp

app = Flask(__name__)
create_tables()
CORS(app)
Swagger(app)

app.register_blueprint(products_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(extras_bp)


@app.before_request
def log_request_info():
    app.logger.info('Headers: %s \n Method: %s\n Request: \n%s', request.headers, request.method,
                    pprint.pformat(request.json, indent=4))


@app.after_request
def log_response_info(response):
    app.logger.info('Response: \n%s', pprint.pformat(response.json, indent=4))
    return response


if __name__ == '__main__':
    app.run(debug=True)
