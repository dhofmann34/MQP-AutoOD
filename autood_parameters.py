import re
from dataclasses import dataclass
from typing import List
from numpy import arange
from outlier_detection_methods import OutlierDetectionMethod

# Default detection parameters
default_N_range = [0.05, 0.07, 0.09, 0.11, 0.13, 0.15]
default_k_range = list(range(10, 110, 10))
default_if_range = [0.5, 0.6, 0.7, 0.8, 0.9]
default_outlier_min = 5
default_outlier_max = 15


@dataclass
class AutoODDefaultParameters:
    dataset: str
    k_range: List[int]
    if_range: List[float]
    N_range: List[int]


autood_datasets_to_parameters = {
    "pageblocks": AutoODDefaultParameters(
        dataset="PageBlocks",
        k_range=list(range(10, 110, 10)),
        if_range=[0.5, 0.6, 0.7, 0.8, 0.9],
        N_range=[0.05, 0.07, 0.09, 0.11, 0.13, 0.15]
    )
}


def get_default_parameters(dataset):
    if dataset in autood_datasets_to_parameters:
        return autood_datasets_to_parameters[dataset]
    return AutoODDefaultParameters(
        dataset=dataset,
        k_range=list(range(10, 110, 10)),
        if_range=[0.5, 0.6, 0.7, 0.8, 0.9],
        N_range=[0.05, 0.07, 0.09, 0.11, 0.13, 0.15]
    )


# Optional arguments include: k_range, if_range
def get_detector_instances(detector: str, outlier_min, outlier_max, **kwargs):
    detector_instances = []
    N_range = default_N_range
    if outlier_min != '' and outlier_max != '':       # Use custom N range
        outlier_min_percent = float(outlier_min) * 0.01
        outlier_max_percent = float(outlier_max) * 0.01
        interval = (outlier_max_percent - outlier_min_percent) / 5
        N_range = [round(x, 5) for x in arange(outlier_min_percent, outlier_max_percent + interval, interval)]

    # If Mahalanobis, the only parameter needed is N_range, so return
    if detector == 'MA':
        instance = {"id": "MA_0",
                    "params": {
                        "N_range": N_range
                    }}
        return [instance]

    k_range = kwargs.get('k_range', None)
    if_range = kwargs.get('if_range', None)

    # If k_range or if_range is not set by the user, use the defaults
    # Iteration list and name is based on which detector is being used
    if detector == 'KNN' or detector == 'LOF':
        if not k_range:
            k_range = default_k_range
        else:
            cleaned_k_range = re.sub(r'[^0-9\s]', ' ', k_range).split(" ")
            processed_k_range = list(filter(lambda x: x != '', cleaned_k_range))
            k_range = list(map(int, processed_k_range))
        iter_list, val = k_range, "k"
    if detector == 'IF':
        if not if_range:
            if_range = default_if_range
        else:
            cleaned_if_range = re.sub(r'[^0-9.0-9\s]', ' ', if_range).split(" ")
            processed_if_range = list(filter(lambda x: x != '', cleaned_if_range))
            if_range = list(map(float, processed_if_range))
        iter_list, val = if_range, "max_features"

    for n in iter_list:
        instance = {"id": detector + "_" + str(n),
                    "params": {
                        f"{val}": n,
                        "N_range": N_range
                    }}
        detector_instances.append(instance)

    return detector_instances


# Parse through input parameters and fill in missing values with defaults
# Return a new dict that follows the correct JSON schema for the DB
def get_detection_parameters(parameters, detection_methods: list):
    detection_parameters = {"global_N_range": default_N_range,
                            "index_col_name": parameters['index_col_name'],
                            "label_col_name": parameters['label_col_name']}
    for method in detection_methods:
        if method == OutlierDetectionMethod.KNN:
            outlier_min = default_outlier_min if parameters['knnMinOutlier'] == '' else parameters['knnMinOutlier']
            outlier_max = default_outlier_max if parameters['knnMaxOutlier'] == '' else parameters['knnMaxOutlier']
            detection_parameters['knn'] = get_detector_instances("KNN", outlier_min, outlier_max,
                                                                 k_range=parameters['knnKRange'])
        elif method == OutlierDetectionMethod.LOF:
            outlier_min = default_outlier_min if parameters['lofMinOutlier'] == '' else parameters['lofMinOutlier']
            outlier_max = default_outlier_max if parameters['lofMaxOutlier'] == '' else parameters['lofMaxOutlier']
            detection_parameters['local_outlier_factor'] = get_detector_instances("LOF", outlier_min, outlier_max,
                                                                                  k_range=parameters['lofKRange'])
        elif method == OutlierDetectionMethod.IsolationForest:
            outlier_min = default_outlier_min if parameters['ifMinOutlier'] == '' else parameters['ifMinOutlier']
            outlier_max = default_outlier_max if parameters['ifMaxOutlier'] == '' else parameters['ifMaxOutlier']
            detection_parameters['isolation_forest'] = get_detector_instances("IF", outlier_min, outlier_max,
                                                                              if_range=parameters['ifRange'])
        elif method == OutlierDetectionMethod.Mahalanobis:
            outlier_min = default_outlier_min if parameters['mMinOutlier'] == '' else parameters['mMinOutlier']
            outlier_max = default_outlier_max if parameters['mMaxOutlier'] == '' else parameters['mMaxOutlier']
            detection_parameters['mahalanobis'] = get_detector_instances("MA", outlier_min, outlier_max)

    return detection_parameters
