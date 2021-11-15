from flask import jsonify, Blueprint, request
from documentation.route import get_doc_path
from resources.service import usuarios as users
from flasgger.utils import swag_from

login_bp = Blueprint("routes-login", __name__)


# @swag_from(get_doc_path("get_extras.yml"))
@login_bp.route('/login', methods=['POST'])
def add_products():
    return users.login(request.json)
