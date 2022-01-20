from flask import jsonify, Blueprint, request
from resources.service import usuarios as users
from flasgger.utils import swag_from

login_bp = Blueprint("routes-login", __name__)


@login_bp.route('/login', methods=['POST'])
def add_products():
    return users.login(request.json)
