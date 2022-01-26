from flasgger import swag_from
from flask import request, jsonify, Blueprint
from resources.service import balance as balance
from resources.service.usuarios import token_required

balance_bp = Blueprint("routes-balance", __name__)


@balance_bp.route('/balance', methods=['GET'])
@token_required
def get_balance():
    return jsonify({"balance": balance.get_balance()})
