import unittest
from autood_parameters import get_detection_parameters
import json
from outlier_detection_methods import OutlierDetectionMethod


def input_params_suite_setup():
    input_params_suite = unittest.TestSuite()
    input_params_suite.addTest(ParameterParsing('get_schema_from_input'))
    return input_params_suite


class ParameterParsing(unittest.TestCase):
    input_params = {}
    detectors = []

    @classmethod
    def setUpClass(cls):
        cls.detectors = [OutlierDetectionMethod.KNN, OutlierDetectionMethod.LOF, OutlierDetectionMethod.IsolationForest]
        with open('\\test_files\\raw_input_params_all.json', 'r') as input_json:
            cls.input_params = json.load(input_json)

    def get_schema_from_input(self):
        self.assertNotEqual(self.input_params, {})
        detection_parameters = get_detection_parameters(self.input_params, self.detectors)
        print(detection_parameters)
        self.assertIsNotNone(detection_parameters)


# Runs the test suites
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(input_params_suite_setup())
