from flask import Blueprint

logs_bp = Blueprint('logs', __name__, url_prefix='/')

from application.logs import routes
