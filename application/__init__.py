"""' This code creates the AutoOD website application.
The code to run the application can be found in wgsi.py.
The default configuration file is configurations.ini.'"""

from flask import Flask
from application import config
from loguru import logger
import collections

collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable

from flask_navigation import Navigation


def create_app(config_file="configurations.ini"):
    app = Flask(__name__)
    app = config.app_config(app)

    with app.app_context():
        # Navigation bar
        nav = Navigation(app)
        nav.Bar('top', [
            nav.Item('Input Page', 'input.autood_form'),
            nav.Item('Result Page', 'results.result_index'),
            nav.Item('About', 'home.about_form'),
            nav.Item('Logs', 'logs.autood_logs')
        ])

        # Set up the logger
        logger.add(app.config['LOGGING_PATH'], format="{time} - {message}")

        # Blueprints
        from application.home import home_bp
        app.register_blueprint(home_bp, url_prefix='/')

        from application.input import input_bp
        app.register_blueprint(input_bp, url_prefix='/')

        from application.results import results_bp
        app.register_blueprint(results_bp, url_prefix='/')

        from application.logs import logs_bp
        app.register_blueprint(logs_bp, url_prefix='/')

        return app
