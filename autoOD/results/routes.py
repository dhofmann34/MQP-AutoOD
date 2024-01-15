import json
import psycopg2
from flask import session, jsonify, render_template
from loguru import logger
from psycopg2 import sql
from autoOD.input.routes import results_global, final_log_filename_global
from autoOD.results import results_bp
from config import get_db_config


@results_bp.route('/autood/result', methods=['GET'])
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


@results_bp.route('/getRunCount', methods=['GET'])
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


@results_bp.route('/getSessionID', methods=['GET'])
def get_session_id():
    user_id = session.get('user_id')
    return user_id


@results_bp.route('/data/<string:session_id>/<int:tab_index>', methods=['GET'])  # get data from DB as json
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


def get_first_run_info():
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    sql_query = sql.get_run_configs(session.get('user_id'), 1)
    cur.execute(sql_query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger.info("Database connection closed successfully.")
    return json.loads(result)
