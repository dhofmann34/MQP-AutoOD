import os
import unittest

import pandas as pd
from loguru import logger
from autoOD.autood import prepare_autood_run_from_params
from autoOD.autood_parameters import get_detection_parameters
import json

from config import get_db_config
from autoOD.outlier_detection_methods import OutlierDetectionMethod


def input_params_suite_setup():
    input_params_suite = unittest.TestSuite()
    input_params_suite.addTest(ParameterParsing('check_result_global_range'))
    input_params_suite.addTest(ParameterParsing('check_knn'))
    input_params_suite.addTest(ParameterParsing('check_lof'))
    input_params_suite.addTest(ParameterParsing('check_if'))
    input_params_suite.addTest(ParameterParsing('check_mahala'))
    input_params_suite.addTest(DetectorMethodsKNN('check_run_KNN'))
    input_params_suite.addTest(DetectorMethodsLOF('check_run_LOF'))
    input_params_suite.addTest(DetectorMethodsIF('check_run_IF'))
    input_params_suite.addTest(DetectorMethodsMA('check_run_MA'))
    return input_params_suite


def get_file(file_prefix='results_pima'):
    for root, directories, files in os.walk("..\\"):
        for file in files:
            if file[0:len(file_prefix)] == file_prefix:
                return os.path.join(root, file)


class ParameterParsing(unittest.TestCase):
    input_params = {}
    detectors = []
    detection_parameters = {}

    @classmethod
    def setUpClass(cls):
        cls.detectors = [OutlierDetectionMethod.KNN, OutlierDetectionMethod.LOF, OutlierDetectionMethod.IsolationForest, OutlierDetectionMethod.Mahalanobis]
        with open("test_files\\raw_input_params_all.json", "r") as input_json:
            cls.input_params = json.load(input_json)
        cls.input_params["index_col_name"] = "id"
        cls.input_params["label_col_name"] = "label"
        cls.detection_parameters = get_detection_parameters(cls.input_params, cls.detectors)

    def check_result_global_range(self):
        self.assertNotEqual(self.input_params, {})
        self.assertIsNotNone(self.detection_parameters)
        self.assertEqual(self.detection_parameters['global_N_range'], [0.05, 0.07, 0.09, 0.11, 0.13, 0.15])
        self.assertEqual(self.detection_parameters['index_col_name'], "id")
        self.assertEqual(self.detection_parameters['label_col_name'], "label")

    def check_knn(self):
        knn = self.detection_parameters['knn']
        self.assertEqual(len(knn), 3)
        self.assertEqual(knn[0]['id'], 'KNN_15')
        self.assertEqual(knn[1]['id'], 'KNN_25')
        self.assertEqual(knn[2]['id'], 'KNN_35')
        self.assertEqual(knn[0]['params']['k'], 15)
        self.assertListEqual(knn[0]['params']['N_range'], [0.05, 0.07, 0.09, 0.11, 0.13, 0.15])

    def check_lof(self):
        lof = self.detection_parameters['local_outlier_factor']
        self.assertEqual(len(lof), 4)
        self.assertEqual(lof[0]['id'], 'LOF_10')
        self.assertEqual(lof[1]['id'], 'LOF_20')
        self.assertEqual(lof[2]['id'], 'LOF_30')
        self.assertEqual(lof[3]['id'], 'LOF_40')
        self.assertEqual(lof[0]['params']['k'], 10)
        self.assertListEqual(lof[0]['params']['N_range'], [0.05, 0.07, 0.09, 0.11, 0.13, 0.15])

    def check_if(self):
        if_ = self.detection_parameters['isolation_forest']
        self.assertEqual(len(if_), 4)
        self.assertEqual(if_[0]['id'], 'IF_0.2')
        self.assertEqual(if_[1]['id'], 'IF_0.3')
        self.assertEqual(if_[2]['id'], 'IF_0.4')
        self.assertEqual(if_[3]['id'], 'IF_1.0')
        self.assertEqual(if_[0]['params']['max_features'], 0.2)
        self.assertListEqual(if_[0]['params']['N_range'], [0.05, 0.07, 0.09, 0.11, 0.13, 0.15])

    def check_mahala(self):
        ma = self.detection_parameters['mahalanobis']
        self.assertEqual(len(ma), 1)
        self.assertEqual(ma[0]['id'], 'MA_0')
        self.assertListEqual(ma[0]['params']['N_range'], [0.05, 0.07, 0.09, 0.11, 0.13, 0.15])


class DetectorMethodsKNN(unittest.TestCase):
    @classmethod
    def setUp(cls):
        filepath = os.path.join('..\\files', 'pima.csv')
        detection_methods = [OutlierDetectionMethod.KNN]
        with open("test_files\\knn_params.json", "r") as input_json:
            cls.detection_parameters = json.load(input_json)
        cls.detection_parameters["index_col_name"] = "id"
        cls.detection_parameters["label_col_name"] = "label"
        logger.add('static/job.log', format="{time} - {message}")
        cls.results = prepare_autood_run_from_params(filepath, logger,
                                                     cls.detection_parameters, detection_methods, get_db_config())

    def check_run_KNN(self):
        self.assertIsNotNone(self.results)
        knn_pima_df = pd.read_csv("output\\" + self.results.results_file_name)
        self.assertEqual(len(knn_pima_df), 768)
        self.assertEqual(self.results.error_message, "")
        self.assertNotEqual(self.results.autood_f1_score, 0)
        self.assertNotEqual(self.results.best_unsupervised_f1_score, 0)
        self.assertListEqual(self.results.best_unsupervised_methods, ["KNN"])


class DetectorMethodsLOF(unittest.TestCase):
    @classmethod
    def setUp(cls):
        filepath = os.path.join('..\\files', 'pima.csv')
        detection_methods = [OutlierDetectionMethod.LOF]
        with open("test_files\\lof_params.json", "r") as input_json:
            cls.detection_parameters = json.load(input_json)
        cls.detection_parameters["index_col_name"] = "id"
        cls.detection_parameters["label_col_name"] = "label"
        logger.add('static/job.log', format="{time} - {message}")
        cls.results = prepare_autood_run_from_params(filepath, logger,
                                                     cls.detection_parameters, detection_methods, get_db_config())

    def check_run_LOF(self):
        self.assertIsNotNone(self.results)
        lof_pima_df = pd.read_csv("output\\" + self.results.results_file_name)
        self.assertEqual(len(lof_pima_df), 768)
        self.assertEqual(self.results.error_message, "")
        self.assertNotEqual(self.results.autood_f1_score, 0)
        self.assertNotEqual(self.results.best_unsupervised_f1_score, 0)
        self.assertListEqual(self.results.best_unsupervised_methods, ["LOF"])


class DetectorMethodsIF(unittest.TestCase):
    @classmethod
    def setUp(cls):
        filepath = os.path.join('..\\files', 'pima.csv')
        detection_methods = [OutlierDetectionMethod.IsolationForest]
        with open("test_files\\if_params.json", "r") as input_json:
            cls.detection_parameters = json.load(input_json)
        cls.detection_parameters["index_col_name"] = "id"
        cls.detection_parameters["label_col_name"] = "label"
        logger.add('static/job.log', format="{time} - {message}")
        cls.results = prepare_autood_run_from_params(filepath, logger,
                                                     cls.detection_parameters, detection_methods, get_db_config())

    def check_run_IF(self):
        self.assertIsNotNone(self.results)
        if_pima_df = pd.read_csv("output\\" + self.results.results_file_name)
        self.assertEqual(len(if_pima_df), 768)
        self.assertEqual(self.results.error_message, "")
        self.assertNotEqual(self.results.autood_f1_score, 0)
        self.assertNotEqual(self.results.best_unsupervised_f1_score, 0)
        self.assertListEqual(self.results.best_unsupervised_methods, ["Isolation_Forest"])


class DetectorMethodsMA(unittest.TestCase):
    @classmethod
    def setUp(cls):
        filepath = os.path.join('..\\files', 'pima.csv')
        detection_methods = [OutlierDetectionMethod.Mahalanobis]
        with open("test_files\\ma_params.json", "r") as input_json:
            cls.detection_parameters = json.load(input_json)
        cls.detection_parameters["index_col_name"] = "id"
        cls.detection_parameters["label_col_name"] = "label"
        logger.add('static/job.log', format="{time} - {message}")
        cls.results = prepare_autood_run_from_params(filepath, logger,
                                                     cls.detection_parameters, detection_methods, get_db_config())

    def check_run_MA(self):
        self.assertIsNotNone(self.results)
        if_pima_df = pd.read_csv("output\\" + self.results.results_file_name)
        self.assertEqual(len(if_pima_df), 768)
        self.assertEqual(self.results.error_message, "")
        self.assertNotEqual(self.results.autood_f1_score, 0)
        self.assertNotEqual(self.results.best_unsupervised_f1_score, 0)
        self.assertListEqual(self.results.best_unsupervised_methods, ["mahalanobis"])


# Runs the test suites
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(input_params_suite_setup())
