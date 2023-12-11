from enum import Enum, auto


class OutlierDetectionMethod(Enum):
    LOF = auto()
    KNN = auto()
    IsolationForest = auto()
    Mahalanobis = auto()
