from flask import jsonify, Blueprint, request
from documentation.route import get_doc_path
from resources.service import extras as extras
from flasgger.utils import swag_from

extras_bp = Blueprint("routes-extras", __name__)


@swag_from(get_doc_path("extras/get_extras.yml"))
@extras_bp.route('/extras', methods=['GET'])
def get_extras():
    exs = extras.get_all_extras()
    return jsonify({"extras": exs})


@swag_from(get_doc_path("extras/put_extras.yml"))
@extras_bp.route('/extras/<int:id_categoria>', methods=['PUT'])
def update_extra(id_categoria):
    extras.update_extra(id_categoria, request.json)
    return jsonify({"mensaje": "editado"})


@swag_from(get_doc_path("extras/post_extras.yml"))
@extras_bp.route('/extras', methods=['POST'])
def add_extra():
    return jsonify({"idextra": extras.add_extra(request.json)})
