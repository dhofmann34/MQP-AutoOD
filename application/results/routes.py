import json
import os
import time
from shutil import copyfile
import psycopg2
from flask import session, jsonify, render_template, request, flash, redirect, current_app
from loguru import logger
import sql_queries
from application.input.input_processing import call_autood_from_params
from application.results import results_bp
from application.results.input_processing import get_detection_methods_from_params, get_first_run_info
from autoOD.autood_parameters import get_detection_parameters
from config import get_db_config
from connect import new_run

global results_global, final_log_filename_global


@results_bp.route('/autood/result', methods=['GET'])
def result_index():
    """If results exist, returns the results."""
    try:
        results = results_global
        final_log_filename = final_log_filename_global
        return render_template('index.html', best_f1=results.best_unsupervised_f1_score,
                               autood_f1=results.autood_f1_score, mv_f1=results.mv_f1_score,
                               best_method=",".join(results.best_unsupervised_methods),
                               final_results=results.results_file_name, training_log=final_log_filename)
    except:
        return render_template('index.html')


@results_bp.route('/autood/result', methods=['POST'])
def autood_rerun():
    """Re-runs AutoOD with dataset from original run and any new input parameters."""
    rerun_params = request.get_json()
    outlier_min = rerun_params['globalMinOutlier']
    outlier_max = rerun_params['globalMaxOutlier']

    # Get run configuration for the first run for filename, index, and label
    first_run_config = get_first_run_info()
    filename = first_run_config['filename']
    index_col_name = first_run_config['index_col_name']
    label_col_name = first_run_config['label_col_name']

    detection_methods = get_detection_methods_from_params(rerun_params)
    if detection_methods is not []:
        rerun_params['index_col_name'] = index_col_name
        rerun_params['label_col_name'] = label_col_name
        run_configuration = get_detection_parameters(rerun_params, detection_methods, outlier_min, outlier_max)
        run_configuration['filename'] = filename
        results = call_autood_from_params(filename, run_configuration, detection_methods)

        # Update the DB with the new run results
        user_id = session.get('user_id')
        new_run(user_id, json.dumps(run_configuration))
        if results.error_message:
            flash(results.error_message)
            return redirect(request.url)
        else:
            # Create empty job.log, old logging will be deleted
            user_id = session.get('user_id')
            final_log_filename = f"log_{filename.replace('.', '_')}_{int(time.time())}_{user_id}"
            output_dir = os.path.join(current_app.config['DOWNLOAD_FOLDER'], final_log_filename)
            copyfile(current_app.config['LOGGING_PATH'], output_dir)
            open(current_app.config['LOGGING_PATH'], 'w').close()
            global results_global, final_log_filename_global
            results_global = results
            final_log_filename_global = final_log_filename
            return render_template('index.html', best_f1=results.best_unsupervised_f1_score,
                                   autood_f1=results.autood_f1_score, mv_f1=results.mv_f1_score,
                                   best_method=",".join(results.best_unsupervised_methods),
                                   final_results=results.results_file_name, training_log=final_log_filename)
    else:
        return redirect(request.url)


@results_bp.route('/getRunCount', methods=['GET'])
def get_run_count():
    user_id = session.get('user_id')
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    sql_query = sql_queries.get_count(user_id)
    cur.execute(sql_query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger.info("Database connection closed successfully.")
    return jsonify(result)


@results_bp.route('/getSessionID', methods=['GET'])
def get_session_id():
    user_id = session.get('user_id')
    return user_id


@results_bp.route('/data/<string:session_id>/<int:tab_index>', methods=['GET'])  # get data from DB as json
def send_data(session_id, tab_index):
    """Returns the run data for specified tab as a json file."""
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    sql_query = sql_queries.get_json(session_id, tab_index)
    cur.execute(sql_query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger.info("Database connection closed successfully.")
    return jsonify(result)
