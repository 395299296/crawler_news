from flask import Blueprint

from . import views, errors

main = Blueprint('main', __name__)

main.add_url_rule('/', 'index', views.index, methods=['GET'])
main.errorhandler(404)(errors.page_not_found)
main.errorhandler(401)(errors.handle_unauthorized)
main.add_url_rule('/<path:invalid_path>', 'handle_unmatchable', errors.handle_unmatchable)
