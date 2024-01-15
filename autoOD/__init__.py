"""' This code creates the AutoOD website application.
The code to run the application can be found in wgsi.py.
The default configuration file is configurations.ini.'"""

from flask import Flask
import config


def create_app(config_file="configurations.ini"):
    app = config.app_config(Flask(__name__))

    # Set up the logger

    # Blueprints
    from home import home_bp
    app.register_blueprint(home_bp, url_prefix='/')

    from input import input_bp
    app.register_blueprint(input_bp, url_prefix='/autood/index')

    from autoOD.results import results_bp
    app.register_blueprint(results_bp, url_prefix='/autood/results')

    return app
