from flask import Blueprint

results_bp = Blueprint('results', __name__, url_prefix='/autood/results')

from autoOD.results import routes
