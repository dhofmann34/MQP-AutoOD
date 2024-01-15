from flask import Blueprint

input_bp = Blueprint('input', __name__, url_prefix='/')

from application.input import routes
