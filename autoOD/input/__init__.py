from flask import Blueprint

input_bp = Blueprint('input', __name__, url_prefix='/autood/index')

from autoOD.input import routes
