import os

from flask import jsonify, Blueprint
from resources.service import extras as extras
from flasgger.utils import swag_from

extras_bp = Blueprint("routes-extras", __name__)

print(os.getcwd())
@swag_from(os.getcwd()+"\documentation\get_extras.yml")
@extras_bp.route('/extras', methods=['GET'])
def add_products():
    exs = extras.get_all_extras()
    return jsonify({"extras": exs})
