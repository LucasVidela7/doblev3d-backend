from flask import jsonify, Blueprint
from documentation.route import get_doc_path
from resources.service import extras as extras
from flasgger.utils import swag_from

extras_bp = Blueprint("routes-extras", __name__)


@swag_from(get_doc_path("get_extras.yml"))
@extras_bp.route('/extras', methods=['GET'])
def add_products():
    exs = extras.get_all_extras()
    return jsonify({"extras": exs})
