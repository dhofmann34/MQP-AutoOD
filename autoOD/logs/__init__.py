from flask import Blueprint

logs_bp = Blueprint('logs', __name__, url_prefix='/')

from autoOD.logs import routes
