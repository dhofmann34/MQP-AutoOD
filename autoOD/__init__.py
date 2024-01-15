"""' This code creates the AutoOD website application.
The code to run the application can be found in wgsi.py.
The default configuration file is configurations.ini.'"""

from flask import Flask
import config
from flask_navigation import Navigation
from loguru import logger
import collections

collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable


def create_app(config_file="configurations.ini"):
    app = config.app_config(Flask(__name__))

    # Navigation bar
    nav = Navigation(app)
    nav.Bar('top', [
        nav.Item('Input Page', 'autood_form'),
        nav.Item('Result Page', 'result_index'),
        nav.Item('About', 'about_form'),
        nav.Item('Logs', 'autood_logs')
    ])

    # Set up the logger
    logger.add(app.config['LOGGING_PATH'], format="{time} - {message}")

    # Blueprints
    from home import home_bp
    app.register_blueprint(home_bp, url_prefix='/')

    from input import input_bp
    app.register_blueprint(input_bp, url_prefix='/autood/index')

    from autoOD.results import results_bp
    app.register_blueprint(results_bp, url_prefix='/autood/results')

    from autoOD.logs import logs_bp
    app.register_blueprint(logs_bp, url_prefix='/')

    return app
