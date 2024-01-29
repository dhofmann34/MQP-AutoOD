import time

from flask import render_template, Response, current_app, send_from_directory, abort, send_file, request
from application.logs import logs_bp

import os

ALLOWED_EXTENSIONS = {'txt'}

def flask_logger(logging_path):
    """creates logging information"""
    with open(logging_path) as log_info:
        while True:
            data = log_info.read()
            yield data.encode()
            time.sleep(1)

def allowed_file(filename):
    if '.' not in filename:
        return True
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@logs_bp.route('/autood/logs', methods=['GET'])
def autood_logs():
    files_directory = current_app.config['DOWNLOAD_FOLDER']
    file_names = [f for f in os.listdir(files_directory) if allowed_file(f) and os.path.isfile(os.path.join(files_directory, f))]
    return render_template('running_logs.html', files=file_names)

@logs_bp.route('/view/<filename>')
def view_file(filename):
    files_directory = current_app.config['DOWNLOAD_FOLDER']
    file_path = os.path.join(files_directory, filename)

    if os.path.exists(file_path) and allowed_file(filename):
        with open(file_path, 'r') as file:
            file_content = file.read()
        return render_template('view_file.html', file_content=file_content, filename=filename)
    else:
        abort(404)

@logs_bp.route("/running_logs", methods=["GET"])
def running_logs():
    """returns logging information"""
    return Response(flask_logger(current_app.config['LOGGING_PATH']), mimetype="text/plain", content_type="text/event-stream")
