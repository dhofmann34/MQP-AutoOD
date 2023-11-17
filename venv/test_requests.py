import unittest
import subprocess
from html.parser import HTMLParser

absolute_path = 'C:\\Users\\tgand\\OneDrive\\Desktop\\WPI Classes\\MQP\\MQP-AutoOD\\results\\'
knn_log_file = absolute_path
all_log_file = absolute_path

knn_links_required = {'/autood/index' : 0, '/autood/results_summary' : 0, '/autood/result': 0, '/autood/about' : 0,
                  '/return-files/*.csv' : 0, '/return-files/log*' : 0}
all_links_required = {'/autood/index' : 0, '/autood/results_summary' : 0, '/autood/result': 0, '/autood/about' : 0,
                  '/return-files/*.csv' : 0, '/return-files/log*' : 0}

# Process logs into a dict (for key/value pairs) and a list (for regular messages)
def process_logs(logs):
    logs_dict = {}
    log_statements = []
    for log in logs:
        log_data = log[33:].strip().split(" = ")  # Ignore timestamp info at start of log entry
        # Handle regular log message (DB connection, training start, error statements)
        if len(log_data) == 1:
            log_statements.append(log_data)
        else: # For logs with format 'key = value', put log values into dict
            logs_dict[log_data[0]] = log_data[1]
    return logs_dict, log_statements


# Test suite of post request tests
def post_suite():
    post_suite = unittest.TestSuite()
    post_suite.addTest(KNNTestCase('test_response'))
    post_suite.addTest(KNNTestCase('test_logs'))
    post_suite.addTest(AllMethodsTestCase('test_response'))
    post_suite.addTest(AllMethodsTestCase('test_logs'))
    return post_suite

class KNNTestCase(unittest.TestCase):
    parser = None
    parsed_response = None

    def setUp(self):
        try:
            self.response = subprocess.check_output(
                'curl -F file="@C:\\Users\\tgand\\OneDrive\\Desktop\\WPI Classes\\MQP\\MQP-AutoOD\\files\\cardio.csv" -F indexColName=id -F labelColName=label -F outlierRangeMin=5 -F outlierRangeMax=15 -F detectionMethods=knn -v "http://localhost:8080/autood/index"',
                timeout=200,
                stderr=subprocess.STDOUT,
                shell=True)
        except subprocess.CalledProcessError:
            self.response = None
            print("POST - KNN | Failed to get a response.")
        self.parser = ResponseParser()

    def test_response(self):
        self.assertIsNotNone(self.response)

        # Parses response HTML
        self.parser.feed(str(self.response))
        self.assertIsNotNone(self.parser.parsed_response)
        print("POST - KNN | Response recieved, verifying correctness")

        i = 0
        num_stylesheets = 0
        global knn_links_required, knn_log_file
        for link_batch in self.parser.parsed_response:
            for link in link_batch:
                if link[1] == 'stylesheet':
                    num_stylesheets += 1
                if link[0] == 'href':
                    results_file = '/return-files/results'
                    log_file = '/return-files/log'
                    css_file = '/static/'
                    if link[1][:len(results_file)] == results_file and link[1][:len(css_file)] != css_file:
                        knn_links_required['/return-files/*.csv'] = 1
                    elif link[1][:len(log_file)] == log_file and link[1][:len(css_file)] != css_file:
                        knn_links_required['/return-files/log*'] = 1
                        knn_log_file += link[1][len(log_file)-3:]
                    elif link[1][:len(css_file)] != css_file:
                        knn_links_required[link[1]] = 1
        # Check that all required links are provided in the response
        self.assertListEqual(list(knn_links_required.values()), [1, 1, 1, 1, 1, 1])
        # Check that the correct number of stylesheets is being used
        self.assertEqual(num_stylesheets, 3)
        print("POST - KNN | All response tests passed")

    def test_logs(self):
        knn_logs = open(knn_log_file, 'r').readlines()
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


class AllMethodsTestCase(unittest.TestCase):
    parser = None
    parsed_response = None

    def setUp(self):
        try:
            methods = ['knn', 'lof', 'if', 'mahala']
            self.response = subprocess.check_output(
                'curl -F file="@C:\\Users\\tgand\\OneDrive\\Desktop\\WPI Classes\\MQP\\MQP-AutoOD\\files\\cardio.csv" -F indexColName=id -F labelColName=label -F outlierRangeMin=5 -F outlierRangeMax=15 -F detectionMethods=knn -F detectionMethods=lof -F detectionMethods=if -F detectionMethods=mahala -v "http://localhost:8080/autood/index"',
                timeout=200,
                stderr=subprocess.STDOUT,
                shell=True)
        except subprocess.CalledProcessError:
            self.response = None
            print("POST - KNN, LOF, IF, MAHALA | Failed to get a response.")
        self.parser = ResponseParser()

    def test_response(self):
        self.assertIsNotNone(self.response)

        # Parses response HTML
        self.parser.feed(str(self.response))
        self.assertIsNotNone(self.parser.parsed_response)
        print("POST - KNN, LOF, IF, MAHALA | Response recieved, verifying correctness")

        i = 0
        num_stylesheets = 0
        global all_links_required, all_log_file
        for link_batch in self.parser.parsed_response:
            for link in link_batch:
                if link[1] == 'stylesheet':
                    num_stylesheets += 1
                if link[0] == 'href':
                    results_file = '/return-files/results'
                    log_file = '/return-files/log'
                    css_file = '/static/'
                    if link[1][:len(results_file)] == results_file and link[1][:len(css_file)] != css_file:
                        all_links_required['/return-files/*.csv'] = 1
                    elif link[1][:len(log_file)] == log_file and link[1][:len(css_file)] != css_file:
                        all_links_required['/return-files/log*'] = 1
                        all_log_file += link[1][len(log_file)-3:]
                    elif link[1][:len(css_file)] != css_file:
                        all_links_required[link[1]] = 1
        # Check that all required links are provided in the response
        self.assertListEqual(list(all_links_required.values()), [1, 1, 1, 1, 1, 1])
        # Check that the correct number of stylesheets is being used
        self.assertEqual(num_stylesheets, 3)
        print("POST - KNN, LOF, IF, MAHALA | All response tests passed")

    def test_logs(self):
        all_logs = open(all_log_file, 'r').readlines()
        all_logs_dict, all_log_statements = process_logs(all_logs)
        self.assertIsNotNone(all_logs_dict)
        self.assertIsNotNone(all_log_statements)
        # Check correct inputs and detection method running
        self.assertEqual(all_logs_dict['selected methods'], "['knn', 'lof', 'if', 'mahala']")
        self.assertEqual(all_logs_dict['Dataset Name'], 'cardio')
        self.assertEqual(all_logs_dict['Dataset size'], '(1831, 21), dataset label size')
        # Check DB connection, no errors with DB, and two rounds of training
        self.assertTrue(['Start running KNN with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'] in all_log_statements)
        self.assertTrue(['Start running Isolation Forest with max feature = [0.5, 0.6, 0.7, 0.8, 0.9]'] in all_log_statements)
        self.assertTrue(['Start running Mahalanobis..'] in all_log_statements)
        self.assertTrue(['Start running LOF with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100]'] in all_log_statements)
        self.assertTrue(['Connecting to the PostgreSQL database...'] in all_log_statements)
        self.assertTrue(['Start First-round AutoOD training...'] in all_log_statements)
        self.assertTrue(['Start Second-round AutoOD training...'] in all_log_statements)
        self.assertTrue(['Database connection closed, inserted successfully.'] in all_log_statements)
        self.assertFalse(['Error connecting to the database or executing query.'] in all_log_statements)
        print("LOGS - KNN, LOF, IF, MAHALA | All tests passed.")

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
    runner.run(post_suite())
