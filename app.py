from flask import Flask, request, render_template, flash, redirect, Response, send_file, session, url_for
import uuid
from werkzeug.utils import secure_filename
import os
from loguru import logger
import time
from shutil import copyfile
import psycopg2
from flask import jsonify
import config
import sql_queries as sql
from autood import prepare_autood_run, OutlierDetectionMethod, prepare_autood_run_from_params
from config import get_db_config
from tqdm import tqdm
from connect import new_session, new_run
from connect import create_session_run_tables
import collections

collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable

results_global = None
final_log_filename_global = None

config.configure_packages()  # not needed when using virtual env
app = Flask(__name__)
app.secret_key = 'secret_key'
app, LOGGING_PATH = config.app_config(app)
logger.add(LOGGING_PATH, format="{time} - {message}")

from flask_cors import CORS
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    create_session_run_tables
    if 'user_id' in session:
        user_id = session['user_id']
        return redirect('/autood/index')
        # return f'Hello returning user! Your user ID is {user_id}'
    else:
        # If 'user_id' is not in the session, generate a new ID and store it
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        new_session(user_id)
        return redirect('/autood/index')
        # return f'Hello new user! Your user ID is {user_id}'


@app.route('/autood/index', methods=['GET'])
def autood_form():
    return render_template('form.html')


@app.route('/autood/logs', methods=['GET'])
def autood_logs():
    return render_template('running_logs.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def flask_logger():
    """creates logging information"""
    with open(LOGGING_PATH) as log_info:
        while True:
            data = log_info.read()
            yield data.encode()
            time.sleep(1)


@app.route("/running_logs", methods=["GET"])
def running_logs():
    """returns logging information"""
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream")


def get_detection_methods(methods: list):
    logger.info(f"selected methods = {methods}")
    name_to_method_map = {
        "lof": OutlierDetectionMethod.LOF,
        "knn": OutlierDetectionMethod.KNN,
        "if": OutlierDetectionMethod.IsolationForest,
        "mahala": OutlierDetectionMethod.Mahalanobis
    }
    selected_methods = [name_to_method_map[method] for method in methods]
    return selected_methods


def get_detection_methods_from_params(parameters: dict):
    selected_methods = []
    name_to_method_map = {
        "lofKRange": OutlierDetectionMethod.LOF,
        "knnKRange": OutlierDetectionMethod.KNN,
        "ifKRange": OutlierDetectionMethod.IsolationForest,
        "runMahalanobis": OutlierDetectionMethod.Mahalanobis
    }
    for name in name_to_method_map:
        if name in parameters:
            if name is "runMahalanobis" and parameters["runMahalanobis"] == "True":
                selected_methods.append(name_to_method_map[name])
            else:
                selected_methods.append(name_to_method_map[name])
    logger.info(f"selected methods = {selected_methods}")
    return selected_methods


@app.route('/autood/result', methods=['POST'])
def autood_rerun():
   print(request.data)
   return redirect(request.url)


@app.route('/autood/index', methods=['POST'])
def autood_input():
    sample_file = request.form['selectedDataset']
    if not sample_file:
        if 'file' not in request.files:
            flash('Please provide an input file or select a dataset.')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Please provide an input file or select a dataset.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        else:
            flash('File type is not supported.')
            return redirect(request.url)

    else:
        filename = sample_file
    # start autoOD computation
    if app.config['ADDITIONAL_INPUTS']:
        # Retrieve parameters from input page
        parameters = request.data
        parameters['index_col_name'] = request.form['indexColName']
        parameters['label_col_name'] = request.form['labelColName']
        detection_methods = get_detection_methods_from_params(parameters)
    else:
        index_col_name = request.form['indexColName']
        label_col_name = request.form['labelColName']
        outlier_range_min = float(request.form['outlierRangeMin'])
        outlier_range_max = float(request.form['outlierRangeMax'])
        detection_methods = get_detection_methods(request.form.getlist('detectionMethods'))
    if not detection_methods:
        flash('Please choose at least one detection method.')
        return redirect(request.url)
    if app.config['ADDITIONAL_INPUTS']:
        results = call_autood_from_params(filename, parameters, detection_methods)
    else:
        results = call_autood(filename, outlier_range_min, outlier_range_max, detection_methods, index_col_name,
                            label_col_name)
    user_id = session.get('user_id')
    new_run(user_id)
    if results.error_message:
        flash(results.error_message)
        return redirect(request.url)
    else:
        # Create empty job.log, old logging will be deleted
        final_log_filename = f"log_{filename.replace('.', '_')}_{int(time.time())}"
        copyfile(LOGGING_PATH, app.config['DOWNLOAD_FOLDER'] + final_log_filename)
        open(LOGGING_PATH, 'w').close()
        global results_global, final_log_filename_global
        results_global = results
        final_log_filename_global = final_log_filename
        return render_template('index.html', best_f1=results.best_unsupervised_f1_score,
                                autood_f1=results.autood_f1_score, mv_f1=results.mv_f1_score,
                                best_method=",".join(results.best_unsupervised_methods),
                                final_results=results.results_file_name, training_log=final_log_filename)

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = app.config['DOWNLOAD_FOLDER'] + filename
    return send_file(file_path, as_attachment=False, attachment_filename='')


def call_autood(filename, outlier_percentage_min, outlier_percentage_max, detection_methods, index_col_name,
                label_col_name):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    logger.info(
        f"Start calling autood with file {filename}...indexColName = {index_col_name}, labelColName = {label_col_name}")
    logger.info(
        f"Parameters: outlier_percentage_min = {outlier_percentage_min}%, outlier_percentage_max = {outlier_percentage_max}%")
    return prepare_autood_run(filepath, logger, outlier_percentage_min, outlier_percentage_max, detection_methods,
                              index_col_name, label_col_name, get_db_config())


# Calling autood with additional user inputs for each detection method
def call_autood_from_params(filename, parameters, detection_methods):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    logger.info(f"Start calling autood with file {filename}...indexColName = " +
                f"{parameters['index_col_name']}, labelColName = {parameters['label_col_name']}")
    #logger.info(
    #     f"Parameters: outlier_percentage_min = {outlier_percentage_min}%, outlier_percentage_max = {outlier_percentage_max}%")
    return prepare_autood_run_from_params(filepath, logger, parameters, detection_methods, get_db_config())


#### DH
from flask_navigation import Navigation

nav = Navigation(app)

nav.Bar('top', [
    nav.Item('Input Page', 'autood_form'),
    nav.Item('Result Page', 'result_index'),
    nav.Item('About', 'about_form'),
    nav.Item('Logs', 'autood_logs')
])


@app.route('/autood/about', methods=['GET'])
def about_form():
    return render_template('about.html')


@app.route('/autood/result', methods=['GET'])
def result_index():
    results = results_global
    final_log_filename = final_log_filename_global
    try:
        return render_template('index.html', best_f1=results.best_unsupervised_f1_score,
                               autood_f1=results.autood_f1_score, mv_f1=results.mv_f1_score,
                               best_method=",".join(results.best_unsupervised_methods),
                               final_results=results.results_file_name, training_log=final_log_filename)
    except:
        return render_template('index.html')

@app.route('/data/<string:session_id>/<int:tab_index>')  # get data from DB as json
def send_data(session_id, tab_index):
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    sql_query = sql.get_json(session_id, tab_index)
    cur.execute(sql_query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger.info("Database connection closed successfully.")
    return jsonify(result)

@app.route('/getRunCount', methods=['GET'])
def get_run_count():
    user_id = session.get('user_id')
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    sql_query = sql.get_count(user_id)
    cur.execute(sql_query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger.info("Database connection closed successfully.")
    return jsonify(result)

@app.route('/getSessionID', methods=['GET'])
def get_session_id():
    user_id = session.get('user_id')
    return user_id

#### DH


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=8080)  # 5000 for VM, 8080 for local machine
