from flask import jsonify, Blueprint, request
from resources.service import extras as extras
from resources.service import categorias as categorias
from flasgger.utils import swag_from

from resources.service.usuarios import token_required

extras_bp = Blueprint("routes-extras", __name__)


@extras_bp.route('/extras', methods=['GET'])
@token_required
def get_extras():
    exs = extras.get_all_extras()
    return jsonify({"extras": exs})


@extras_bp.route('/extras/<int:id_extra>', methods=['PUT'])
@token_required
def update_extra(id_extra):
    extras.update_extra(id_extra, request.json)
    return jsonify({"idextra": id_extra, "status": True})


@extras_bp.route('/extras/<int:id_extra>', methods=['GET'])
@token_required
def get_extra(id_extra):
    ex = extras.select_extra_by_id(id_extra)
    categories_by_extra = categorias.get_categories_by_extras(id_extra)
    return jsonify({"categorias": categories_by_extra, "extra": ex})


@extras_bp.route('/extras/<int:id_extra>', methods=['DELETE'])
@token_required
def delete_extra(id_extra):
    extras.delete_extra(id_extra)
    return jsonify({"status": True})


@extras_bp.route('/extras', methods=['POST'])
@token_required
def add_extra():
    return jsonify({"idextra": extras.add_extra(request.json), "status": True})

# @extras_bp.route('/extrasByIDCategoria/<int:id_categoria>', methods=['GET'])
# @token_required
# def get_extras_by_id_categoria(id_categoria):
#     categories_by_extra = extras.select_extra_by_id_categoria(id_categoria)
#     return jsonify({"extras": categories_by_extra})
