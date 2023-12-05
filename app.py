from flask import Flask, request, render_template, flash, redirect, Response, send_file
from werkzeug.utils import secure_filename
import os
from loguru import logger
import time
from shutil import copyfile
import psycopg2
from flask import jsonify
import config
import sql_queries as sql
from autood import run_autood, OutlierDetectionMethod
from config import get_db_config
from tqdm import tqdm
import collections
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable

results_global = None
final_log_filename_global = None


config.configure_packages()  # not needed when using virtual env
app = Flask(__name__)
app, LOGGING_PATH = config.app_config(app)
logger.add(LOGGING_PATH, format="{time} - {message}")


@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect('/autood/index')


@app.route('/autood/results_summary', methods=['GET'])  # DH
def results1():
    results = results_global
    final_log_filename = final_log_filename_global
    try:
        return render_template('result_summary.html', best_f1=results.best_unsupervised_f1_score,
                               autood_f1=results.autood_f1_score, mv_f1=results.mv_f1_score,
                               best_method=",".join(results.best_unsupervised_methods),
                               final_results=results.results_file_name, training_log=final_log_filename)
    except:
        return render_template('result_summary.html')


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


def get_detection_methods(methods):
    logger.info(f"selected methods = {methods}")
    name_to_method_map = {
        "lof": OutlierDetectionMethod.LOF,
        "knn": OutlierDetectionMethod.KNN,
        "if": OutlierDetectionMethod.IsolationForest,
        "mahala": OutlierDetectionMethod.Manalanobis
    }
    selected_methods = [name_to_method_map[method] for method in methods]
    return selected_methods


@app.route('/autood/index', methods=['POST'])
def autood_input():
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
        # start autoOD computation
        index_col_name = request.form['indexColName']
        label_col_name = request.form['labelColName']
        outlier_range_min = float(request.form['outlierRangeMin'])
        outlier_range_max = float(request.form['outlierRangeMax'])
        detection_methods = get_detection_methods(request.form.getlist('detectionMethods'))
        if not detection_methods:
            flash('Please choose at least one detection method.')
            return redirect(request.url)
        results = call_autood(filename, outlier_range_min, outlier_range_max, detection_methods, index_col_name,
                              label_col_name)
        if results.error_message:
            flash(results.error_message)
            return redirect(request.url)
        else:
            # Create empty job.log, old logging will be deleted
            final_log_filename = f"log_{file.filename.replace('.', '_')}_{int(time.time())}"
            copyfile(LOGGING_PATH, app.config['DOWNLOAD_FOLDER'] + final_log_filename)
            open(LOGGING_PATH, 'w').close()
            global results_global, final_log_filename_global
            results_global = results
            final_log_filename_global = final_log_filename
            return render_template('index.html', best_f1=results.best_unsupervised_f1_score,
                                   autood_f1=results.autood_f1_score, mv_f1=results.mv_f1_score,
                                   best_method=",".join(results.best_unsupervised_methods),
                                   final_results=results.results_file_name, training_log=final_log_filename)
    else:
        flash('File type is not supported.')
        return redirect(request.url)


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
    return run_autood(filepath, logger, outlier_percentage_min, outlier_percentage_max, detection_methods,
                      index_col_name, label_col_name, get_db_config())


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
    return render_template('index.html')


@app.route('/data')  # get data from DB as json
def send_data():
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    # we can use multiple execute statements to get the data how we need it
    cur.execute(sql.ITERATIONS_FROM_RELIABLE_TABLE)  # number of iterations for reliable labels
    iteration = cur.fetchall()[0][0] + 1
    cur.close()
    cur = conn.cursor()

    # drop all tables on each run
    cur.execute(sql.DROP_ALL_TEMP_TABLES)

    # create temp tables so that we can pass the data in a way that JS/D3 needs it
    cur.execute(sql.CREATE_TEMP_LOF_TABLE)

    cur.execute(sql.CREATE_TEMP_KNN_TABLE)

    cur.execute(sql.CREATE_TEMP_IF_TABLE)

    cur.execute(sql.CREATE_TEMP_MAHALANOBIS_TABLE)

    cur.execute(sql.CREATE_REALIABLE_TABLES(iteration))

    # Join all tables together
    SQL_statement = sql.JOIN_ALL_TABLES
    join_reliable = sql.JOIN_RELIABLE_TABLES(iteration)

    cur.execute(f"{SQL_statement}{join_reliable}")

    # data = [col for col in cur]
    field_names = [i[0] for i in cur.description]
    result = [dict(zip(field_names, row)) for row in cur.fetchall()]
    # conn.commit()
    cur.close()
    conn.close()
    logger.info("Database connection closed successfully.")
    return jsonify(result)


#### DH


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=8080)  # 5000 for VM, 8080 for local machine
