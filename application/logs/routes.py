import time

from flask import render_template, Response, current_app

from application.logs import logs_bp


def flask_logger(logging_path):
    """creates logging information"""
    with open(logging_path) as log_info:
        while True:
            data = log_info.read()
            yield data.encode()
            time.sleep(1)


@logs_bp.route('/autood/logs', methods=['GET'])
def autood_logs():
    return render_template('running_logs.html')


@logs_bp.route("/running_logs", methods=["GET"])
def running_logs():
    """returns logging information"""
    return Response(flask_logger(current_app.config['LOGGING_PATH']), mimetype="text/plain", content_type="text/event-stream")
