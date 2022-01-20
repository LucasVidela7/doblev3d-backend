from flasgger import swag_from
from flask import request, jsonify, Blueprint
from documentation.route import get_doc_path
from resources.service import balance as balance

balance_bp = Blueprint("routes-balance", __name__)


@balance_bp.route('/balance', methods=['GET'])
def get_balance():
    return jsonify({"balance": balance.get_balance()})
