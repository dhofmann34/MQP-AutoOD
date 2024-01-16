"""The home blueprint includes / route. It also includes the about page."""

from flask import Blueprint

home_bp = Blueprint('home', __name__, url_prefix='/')

from application.home import routes
