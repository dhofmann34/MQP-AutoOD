from flask import Blueprint

results_bp = Blueprint('results', __name__, url_prefix='/')

from autoOD.results import routes
