from flask import current_app
from outlier_detection_methods import OutlierDetectionMethod


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def get_detection_methods(methods: list):
    # logger.info(f"selected methods = {methods}")
    name_to_method_map = {
        "lof": OutlierDetectionMethod.LOF,
        "knn": OutlierDetectionMethod.KNN,
        "if": OutlierDetectionMethod.IsolationForest,
        "mahala": OutlierDetectionMethod.Mahalanobis
    }
    selected_methods = [name_to_method_map[method] for method in methods]
    return selected_methods
