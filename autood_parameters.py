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
        outlier_min_percent = outlier_min * 0.01
        outlier_max_percent = outlier_max * 0.01
        interval = (outlier_max_percent - outlier_min_percent) / 5
        N_range = [round(x, 5) for x in arange(outlier_min_percent, outlier_max_percent + interval, interval)]

    k_range = kwargs.get('k_range', None)
    if_range = kwargs.get('if_range', None)
    if (detector == 'KNN' or detector == 'LOF') and k_range == []:
        k_range = default_k_range
    if detector == 'IF' and if_range == []:
        if_range = default_if_range

    iter_list, val = k_range, "k" if k_range is not None else if_range, "max_features"
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
    detection_parameters = {"global_N_range": default_N_range}
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
        # elif method == OutlierDetectionMethod.Mahalanobis:

    return detection_parameters
