import unittest
from autood_parameters import get_detection_parameters
import json
from outlier_detection_methods import OutlierDetectionMethod


def input_params_suite_setup():
    input_params_suite = unittest.TestSuite()
    input_params_suite.addTest(ParameterParsing('check_result_global_range'))
    input_params_suite.addTest(ParameterParsing('check_knn'))
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


# Runs the test suites
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(input_params_suite_setup())
