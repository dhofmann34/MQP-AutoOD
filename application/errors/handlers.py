"""The following error handlers will catch handle HTTP exceptions from the website.
User-friendly error templates should be shown instead of the default Flask templates."""
from application.errors import errors_bp
from flask import Flask, render_template


@errors_bp.app_errorhandler(400)
def generic_bad_request(e):
    return render_template('error.html'), 400


@errors_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@errors_bp.app_errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html'), 405


@errors_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error.html'), 500
