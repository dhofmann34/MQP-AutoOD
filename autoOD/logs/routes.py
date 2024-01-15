import time

from flask import render_template, Response, current_app

from autoOD.logs import logs_bp


def flask_logger():
    """creates logging information"""
    with open(current_app['LOGGING_PATH']) as log_info:
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
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream")
