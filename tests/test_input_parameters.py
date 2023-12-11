import unittest
from autood_parameters import get_detection_parameters
import json
from outlier_detection_methods import OutlierDetectionMethod


def input_params_suite_setup():
    input_params_suite = unittest.TestSuite()
    input_params_suite.addTest(ParameterParsing('check_result_global_range'))
    input_params_suite.addTest(ParameterParsing('check_knn'))
    input_params_suite.addTest(ParameterParsing('check_lof'))
    input_params_suite.addTest(ParameterParsing('check_if'))
    return input_params_suite


class ParameterParsing(unittest.TestCase):
    input_params = {}
    detectors = []
    detection_parameters = {}

    @classmethod
    def setUpClass(cls):
        cls.detectors = [OutlierDetectionMethod.KNN, OutlierDetectionMethod.LOF, OutlierDetectionMethod.IsolationForest]
        with open("test_files\\raw_input_params_all.json", "r") as input_json:
            cls.input_params = json.load(input_json)
        cls.detection_parameters = get_detection_parameters(cls.input_params, cls.detectors)

    def check_result_global_range(self):
        self.assertNotEqual(self.input_params, {})
        self.assertIsNotNone(self.detection_parameters)
        self.assertEqual(self.detection_parameters['global_N_range'], [0.05, 0.07, 0.09, 0.11, 0.13, 0.15])

    def check_knn(self):
        knn = self.detection_parameters['knn']
        self.assertEqual(len(knn), 3)
        self.assertEqual(knn[0]['id'], 'KNN_15')
        self.assertEqual(knn[1]['id'], 'KNN_25')
        self.assertEqual(knn[2]['id'], 'KNN_35')
        self.assertEqual(knn[0]['params']['k'], 15)
        self.assertListEqual(knn[0]['params']['N_range'], [0.02, 0.036, 0.052, 0.068, 0.084, 0.1])

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


class DetectorMethods(unittest.TestCase):
    @classmethod
    def setUp(cls):
        print("setup")


# Runs the test suites
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(input_params_suite_setup())
