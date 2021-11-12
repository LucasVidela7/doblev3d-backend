from flask import Flask
from flask_cors import CORS

from database.setup import create_tables
from resources.controller.products import products_bp
from resources.controller.categorias import categorias_bp

app = Flask(__name__)
create_tables()
CORS(app)

# Blueprints
app.register_blueprint(products_bp)
app.register_blueprint(categorias_bp)


if __name__ == '__main__':
    app.run(debug=True)