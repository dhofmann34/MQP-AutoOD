"""The following error handlers will catch handle HTTP exceptions from the website.
User-friendly error templates should be shown instead of the default Flask templates."""
from application.errors import errors_bp


@errors_bp.app_errorhandler(400)
def generic_bad_request(e):
    return "Oops...please reload the page"


@errors_bp.app_errorhandler(404)
def page_not_found(e):
    return "Page not found"


@errors_bp.app_errorhandler(405)
def method_not_allowed(e):
    return "Method not allowed"


@errors_bp.app_errorhandler(500)
def internal_server_error(e):
    return "Please reload the page"
