import unittest
import subprocess
from html.parser import HTMLParser
import pandas as pd
import os


# Temporary function to find results and logs files -- need a clean results folder.
# Will use most recent results and log files
# file_type: log, results
def get_file(path, file_type='log'):
    for root, directories, files in os.walk(path):
        for file in files:
            if file_type == 'log' and file[0:3] == file_type:
                return os.path.join(root, file)
            elif file_type == 'results' and file[0:7] == file_type:
                return os.path.join(root, file)


# Absolute path to results folder
absolute_path = "..\\output\\"
filepaths = {'knn_logs': absolute_path,
             'all_logs': absolute_path,
             'knn_results': absolute_path,
             'all_results': absolute_path,
             'all_results_standard': absolute_path + "all_methods_cardio_standard.csv",
             'knn_results_standard': absolute_path + "knn_cardio_standard.csv"}

# Links required in every results summary page
knn_links_required = {'/autood/index': 0, '/autood/result': 0, '/autood/about': 0, '/autood/logs': 0}
all_links_required = {'/autood/index': 0, '/autood/result': 0, '/autood/about': 0, '/autood/logs': 0}


# Process logs into a dict (for key/value pairs) and a list (for regular messages)
def process_logs(logs):
    logs_dict = {}
    log_statements = []
    for log in logs:
        log_data = log[33:].strip().split(" = ")  # Ignore timestamp info at start of log entry
        # Handle regular log message (DB connection, training start, error statements)
        if len(log_data) == 1:
            log_statements.append(log_data)
        else:  # For logs with format 'key = value', put log values into dict
            logs_dict[log_data[0]] = log_data[1]
    return logs_dict, log_statements


# Process parsed responses, return the number of style sheets and set global variables
def process_parsed_response(parsed_response, all_methods=False):
    global knn_links_required, all_links_required, filepaths
    num_stylesheets = 0

    for link_batch in parsed_response:
        for link in link_batch:
            if link[1] == 'stylesheet':
                num_stylesheets += 1
            if link[0] == 'href':  # Links
                css_file = '/static/'
                # If the link is not a css file, mark it as seen (1)
                if link[1][:len(css_file)] != css_file:
                    if all_methods:
                        all_links_required[link[1]] = 1
                    else:
                        knn_links_required[link[1]] = 1
    return num_stylesheets


# Test suite of post request tests
def post_suite_setup():
    post_suite = unittest.TestSuite()
    # post_suite.addTest(KNNTestCase('test_response'))
    # post_suite.addTest(KNNTestCase('test_logs'))
    # post_suite.addTest(KNNTestCase('test_results'))
    post_suite.addTest(AllMethodsTestCase('test_response'))
    post_suite.addTest(AllMethodsTestCase('test_logs'))
    post_suite.addTest(AllMethodsTestCase('test_results'))
    return post_suite


class KNNTestCase(unittest.TestCase):
    parser = None
    parsed_response = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.response = subprocess.check_output(
                'curl -F file="@C:\\Users\\tgand\\OneDrive\\Desktop\\WPI Classes\\MQP\\MQP-AutoOD\\files\\cardio.csv" '
                '-F indexColName=id -F labelColName=label -F outlierRangeMin=5 -F outlierRangeMax=15 -F '
                'detectionMethods=knn -v "http://localhost:8080/autood/index"',
                timeout=200,
                stderr=subprocess.STDOUT,
                shell=True)
        except subprocess.CalledProcessError:
            cls.response = None
            print("POST - KNN | Failed to get a response.")
        cls.parser = ResponseParser()

    def test_response(self):
        self.assertIsNotNone(self.response)

        # Parses response HTML
        self.parser.feed(str(self.response))
        self.assertIsNotNone(self.parser.parsed_response)
        print("POST - KNN | Response recieved, verifying correctness.")

        num_stylesheets = process_parsed_response(self.parser.parsed_response, all_methods=False)

        global knn_links_required
        # Check that all required links are provided in the response
        self.assertEqual(knn_links_required['/autood/index'], 1)
        self.assertEqual(knn_links_required['/autood/result'], 1)
        self.assertEqual(knn_links_required['/autood/about'], 1)
        self.assertEqual(knn_links_required['/autood/logs'], 1)
        # Check that the correct number of stylesheets is being used
        self.assertEqual(num_stylesheets, 3)
        print("POST - KNN | All response tests passed.")

    def test_logs(self):
        # global filepaths
        # knn_logs = open(filepaths['knn_logs'], 'r').readlines()
        knn_logs = open(get_file(absolute_path, file_type='log'), 'r').readlines()
        knn_logs_dict, knn_log_statements = process_logs(knn_logs)
        self.assertIsNotNone(knn_logs_dict)
        self.assertIsNotNone(knn_log_statements)

        # Check correct inputs and detection method running
        self.assertEqual(knn_logs_dict['selected methods'], "['knn']")
        self.assertEqual(knn_logs_dict['Dataset Name'], 'cardio')
        self.assertEqual(knn_logs_dict['Dataset size'], '(1831, 21), dataset label size')

        # Check DB connection, no errors with DB, and two rounds of training
        self.assertTrue(['Start running KNN with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'] in knn_log_statements)
        self.assertTrue(['Connecting to the PostgreSQL database...'] in knn_log_statements)
        self.assertTrue(['Start First-round AutoOD training...'] in knn_log_statements)
        self.assertTrue(['Start Second-round AutoOD training...'] in knn_log_statements)
        self.assertTrue(['Database connection closed, inserted successfully.'] in knn_log_statements)
        self.assertFalse(['Error connecting to the database or executing query.'] in knn_log_statements)
        print("LOGS - KNN | All tests passed.")

    # Compares response predictions with correct predictions
    def test_results(self):
        knn_df = pd.read_csv(filepaths['knn_results_standard'])
        # all_response_df = pd.read_csv(filepaths['knn_results'])
        knn_response_df = pd.read_csv(get_file(absolute_path, file_type='results'))
        diff_df = knn_df.compare(knn_response_df, result_names=("Correct Result", "Test Result"))
        if not diff_df.empty:
            print("PREDICTIONS - KNN | Outlier predictions are not correct. Review results.")
            print(diff_df)
        self.assertTrue(diff_df.empty)
        print("PREDICTIONS - KNN | Outlier predictions are correct.")


class AllMethodsTestCase(unittest.TestCase):
    parser = None
    parsed_response = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.response = subprocess.check_output(
                'curl -F file="@C:\\Users\\tgand\\OneDrive\\Desktop\\WPI Classes\\MQP\\MQP-AutoOD\\files\\cardio.csv" '
                '-F indexColName=id -F labelColName=label -F outlierRangeMin=5 -F outlierRangeMax=15 -F '
                'detectionMethods=knn -F detectionMethods=lof -F detectionMethods=if -F detectionMethods=mahala -v '
                '"http://localhost:8080/autood/index"',
                timeout=200,
                stderr=subprocess.STDOUT,
                shell=True)
        except subprocess.CalledProcessError:
            cls.response = None
            print("POST - KNN, LOF, IF, MAHALA | Failed to get a response.")
        cls.parser = ResponseParser()

    def test_response(self):
        self.assertIsNotNone(self.response)

        # Parses response HTML
        self.parser.feed(str(self.response))
        self.assertIsNotNone(self.parser.parsed_response)
        print("POST - KNN, LOF, IF, MAHALA | Response recieved, verifying correctness.")

        num_stylesheets = process_parsed_response(self.parser.parsed_response, all_methods=True)

        global all_links_required
        # Check that all required links are provided in the response
        self.assertEqual(all_links_required['/autood/index'], 1)
        self.assertEqual(all_links_required['/autood/result'], 1)
        self.assertEqual(all_links_required['/autood/about'], 1)
        self.assertEqual(all_links_required['/autood/logs'], 1)
        # Check that the correct number of stylesheets is being used
        self.assertEqual(num_stylesheets, 3)
        print("POST - KNN, LOF, IF, MAHALA | All response tests passed.")

    def test_logs(self):
        # global filepaths
        # all_logs = open(filepaths['all_logs'], 'r').readlines()
        all_logs = open(get_file(absolute_path, file_type='log'), 'r').readlines()
        all_logs_dict, all_log_statements = process_logs(all_logs)
        self.assertIsNotNone(all_logs_dict)
        self.assertIsNotNone(all_log_statements)

        # Check correct inputs and detection method running
        self.assertEqual(all_logs_dict['selected methods'], "['knn', 'lof', 'if', 'mahala']")
        self.assertEqual(all_logs_dict['Dataset Name'], 'cardio')
        self.assertEqual(all_logs_dict['Dataset size'], '(1831, 21), dataset label size')
        self.assertEqual(all_logs_dict['Start running Isolation Forest with max feature'], "[0.5, 0.6, 0.7, 0.8, 0.9]")

        # Check DB connection, no errors with DB, and two rounds of training
        self.assertTrue(['Start running KNN with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'] in all_log_statements)
        self.assertTrue(['Start running Mahalanobis..'] in all_log_statements)
        self.assertTrue(['Start running LOF with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'] in all_log_statements)
        self.assertTrue(['Connecting to the PostgreSQL database...'] in all_log_statements)
        self.assertTrue(['Start First-round AutoOD training...'] in all_log_statements)
        self.assertTrue(['Start Second-round AutoOD training...'] in all_log_statements)
        self.assertTrue(['Database connection closed, inserted successfully.'] in all_log_statements)
        self.assertFalse(['Error connecting to the database or executing query.'] in all_log_statements)
        print("LOGS - KNN, LOF, IF, MAHALA | All tests passed.")

    # Compares response predictions with correct predictions
    def test_results(self):
        all_df = pd.read_csv(filepaths['all_results_standard'])
        # all_response_df = pd.read_csv(filepaths['all_results'])
        all_response_df = pd.read_csv(get_file(absolute_path, file_type='results'))
        diff_df = all_df.compare(all_response_df, result_names=("Correct Result", "Test Result"))
        if not diff_df.empty:
            print("PREDICTIONS - KNN, LOF, IF, MAHALA | Outlier predictions are not correct. Review results.")
            print(diff_df)
        self.assertTrue(diff_df.empty)
        print("PREDICTIONS - KNN, LOF, IF, MAHALA | Outlier predictions are correct.")


# Parses HTML response
class ResponseParser(HTMLParser):
    parsed_response = []

    def __init__(self):
        HTMLParser.__init__(self)
        self.parsed_response = []

    # Handles the start tag of the response (ex: <href ... >)
    def handle_starttag(self, tag, attrs):
        if tag == 'link' or tag == 'a':
            self.parsed_response.append(attrs)


# Runs the test suites
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(post_suite_setup())