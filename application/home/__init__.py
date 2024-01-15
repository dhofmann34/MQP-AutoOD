"""''The home blueprint includes / route. It also includes routes not exposed to the end user.
See routes.py for more details."""

from flask import Blueprint

bp = Blueprint('home', __name__, url_prefix='/')

from application.home import routes
