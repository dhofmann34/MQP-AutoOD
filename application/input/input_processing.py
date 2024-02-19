import logging
import os
import time
from flask import current_app, session
from loguru import logger
from autoOD.autood import prepare_autood_run_from_params
from autoOD.autood_parameters import get_detection_parameters
from config import get_db_config
from autoOD.outlier_detection_methods import OutlierDetectionMethod


def allowed_file(filename):
    """Check if the file is valid according to config's allowed extensions."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def get_detection_methods(methods: list):
    """Transforms the methods in the list into OutlierDetectionMethod objects.
    Arguments:
        methods -- the list sent from the input page's form
    """
    #logs
    user_id = session.get('user_id')
    session_logger = logging.getLogger(f"session_{user_id}")
    session_logger.setLevel(logging.INFO)

    session_logger.info(f"selected methods = {methods}")
    name_to_method_map = {
        "lof": OutlierDetectionMethod.LOF,
        "knn": OutlierDetectionMethod.KNN,
        "if": OutlierDetectionMethod.IsolationForest,
        "mahala": OutlierDetectionMethod.Mahalanobis
    }
    selected_methods = [name_to_method_map[method] for method in methods]
    return selected_methods


# Get the dict for the run configuration that is expected by the DB
def get_default_run_configuration(run_configuration, detection_methods, outlier_range_min, outlier_range_max):
    """Get the default run configuration dict from selected detection methods.
    Arguments:
        run_configuration -- dict
        detection_methods -- list of OutlierDetectionMethod objects
        outlier_range_min -- (int) minimum percentage
        outlier_range_max -- (int) maximum percentage
    """
    if OutlierDetectionMethod.LOF in detection_methods:
        run_configuration["lofKRange"] = ""
    if OutlierDetectionMethod.KNN in detection_methods:
        run_configuration["knnKRange"] = ""
    if OutlierDetectionMethod.IsolationForest in detection_methods:
        run_configuration["ifRange"] = ""
    if OutlierDetectionMethod.Mahalanobis in detection_methods:
        run_configuration["runMahalanobis"] = True
    #logs
    user_id = session.get('user_id')
    session_logger = logging.getLogger(f"session_{user_id}")
    session_logger.info(
         f"Parameters: outlier_percentage_min = {outlier_range_min}%, outlier_percentage_max = {outlier_range_max}%")
    return get_detection_parameters(run_configuration, detection_methods, outlier_range_min, outlier_range_max)


# Calling autood with additional user inputs for each detection method
def call_autood_from_params(filename, run_configuration, detection_methods):
    """Call autood.py with required arguments."""
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    #logs
    user_id = session.get('user_id')
    session_logger = logging.getLogger(f"session_{user_id}")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s - %(message)s")
    outputpath = f'{current_app.config["DOWNLOAD_FOLDER"]}/{user_id}_{int(time.time())}_{filename}.log'
    file_handler = logging.FileHandler(outputpath)
    file_handler.setFormatter(formatter)
    session_logger.addHandler(file_handler)
    session_logger.info(f"Start calling autood with file {filename}...indexColName = " +
                f"{run_configuration['index_col_name']}, labelColName = {run_configuration['label_col_name']}")
    return prepare_autood_run_from_params(filepath, session_logger, run_configuration, detection_methods, get_db_config())
