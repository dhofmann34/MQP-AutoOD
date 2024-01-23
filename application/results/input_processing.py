import json

import psycopg2
from flask import session
from loguru import logger

import sql_queries
from autoOD.outlier_detection_methods import OutlierDetectionMethod
from config import get_db_config


def get_detection_methods_from_params(parameters: dict):
    selected_methods = []
    name_to_method_map = {
        "lofKRange": OutlierDetectionMethod.LOF,
        "knnKRange": OutlierDetectionMethod.KNN,
        "ifRange": OutlierDetectionMethod.IsolationForest,
        "runMahalanobis": OutlierDetectionMethod.Mahalanobis
    }
    for name in name_to_method_map:
        if name in parameters:
            if name == "runMahalanobis" and parameters["runMahalanobis"] == "True":
                selected_methods.append(name_to_method_map[name])
            else:
                selected_methods.append(name_to_method_map[name])
    logger.info(f"selected methods = {selected_methods}")
    return selected_methods


def get_first_run_info(current_run):
    conn = psycopg2.connect(**get_db_config())
    cur = conn.cursor()
    sql_query = sql_queries.get_run_configs(session.get('user_id'), current_run)
    cur.execute(sql_query)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    logger.info("Database connection closed successfully.")
    return json.loads(result)
