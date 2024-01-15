from loguru import logger

from autoOD.outlier_detection_methods import OutlierDetectionMethod


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
