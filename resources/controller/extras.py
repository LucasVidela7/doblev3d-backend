from flask import jsonify, Blueprint, request
from documentation.route import get_doc_path
from resources.service import extras as extras
from resources.service import categorias as categorias
from flasgger.utils import swag_from

extras_bp = Blueprint("routes-extras", __name__)


@swag_from(get_doc_path("extras/get_extras.yml"))
@extras_bp.route('/extras', methods=['GET'])
def get_extras():
    exs = extras.get_all_extras()
    return jsonify({"extras": exs})


@swag_from(get_doc_path("extras/put_extras.yml"))
@extras_bp.route('/extras/<int:id_extra>', methods=['PUT'])
def update_extra(id_extra):
    extras.update_extra(id_extra, request.json)
    return jsonify({"mensaje": "editado"})


@swag_from(get_doc_path("extras/get_extra_by_id.yml"))
@extras_bp.route('/extras/<int:id_extra>', methods=['GET'])
def get_extra(id_extra):
    ex = extras.select_extra_by_id(id_extra)
    categories_by_extra = categorias.get_categories_by_extras(id_extra)
    return jsonify({"categorias": categories_by_extra, "extra": ex})


@swag_from(get_doc_path("extras/delete_extras.yml"))
@extras_bp.route('/extras/<int:id_extra>', methods=['DELETE'])
def delete_extra(id_extra):
    extras.delete_extra(id_extra)
    return jsonify({"mensaje": "borrado"})


@swag_from(get_doc_path("extras/post_extras.yml"))
@extras_bp.route('/extras', methods=['POST'])
def add_extra():
    return jsonify({"idextra": extras.add_extra(request.json)})


@swag_from(get_doc_path("extras/get_extra_by_id_categoria.yml"))
@extras_bp.route('/extrasByIDCategoria/<int:id_categoria>', methods=['GET'])
def get_extras_by_id_categoria(id_categoria):
    categories_by_extra = extras.select_extra_by_id_categoria(id_categoria)
    return jsonify({"extras": categories_by_extra})
