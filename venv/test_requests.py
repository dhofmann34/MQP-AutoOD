import unittest
import subprocess
from html.parser import HTMLParser

# TODO: change all print statements to log statements

# Test suite of post request tests
def post_suite():
    post_suite = unittest.TestSuite()
    post_suite.addTest(KNNTestCase('test_response'))
    # Each detection method individually
    # 2 of them together
    # all 4 of them
    return post_suite

def log_suite():
    # check the output logs from post calls
    return log_suite()

class KNNTestCase(unittest.TestCase):
    parser = None
    links_required = None
    parsed_response = None

    def setUp(self):
        # try:
        #     self.response = subprocess.check_output(
        #         'curl -F file="@C:\\Users\\tgand\\OneDrive\\Desktop\\WPI Classes\\MQP\\MQP-AutoOD\\files\\cardio.csv" -F indexColName=id -F labelColName=label -F outlierRangeMin=5 -F outlierRangeMax=15 -F detectionMethods=knn -v "http://localhost:8080/autood/index"',
        #         timeout=200,
        #         stderr=subprocess.STDOUT,
        #         shell=True)
        # except subprocess.CalledProcessError:
        #     self.response = None
        #     print("Post request with KNN failed to get a response.")
        self.links_required = {'/autood/index' : 0,
                               '/autood/results_summary' : 0,
                               '/autood/result': 0,
                               '/autood/about' : 0,
                               '/return-files/*.csv' : 0,
                               '/return-files/log*' : 0}
        self.parser = ResponseParser()
        self.response = b'  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\r\n                                 Dload  Upload   Total   Spent    Left  Speed\r\n\r  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying 127.0.0.1:8080...\r\n* Connected to localhost (127.0.0.1) port 8080 (#0)\r\n> POST /autood/index HTTP/1.1\r\r\n> Host: localhost:8080\r\r\n> User-Agent: curl/8.0.1\r\r\n> Accept: */*\r\r\n> Content-Length: 496817\r\r\n> Content-Type: multipart/form-data; boundary=------------------------b8d4a8b94ff89513\r\r\n> \r\r\n} [65536 bytes data]\r\n* We are completely uploaded and fine\r\n\r100  485k    0     0  100  485k      0   394k  0:00:01  0:00:01 --:--:--  395k\r100  485k    0     0  100  485k      0   216k  0:00:02  0:00:02 --:--:--  216k\r100  485k    0     0  100  485k      0   149k  0:00:03  0:00:03 --:--:--  149k\r100  485k    0     0  100  485k      0   114k  0:00:04  0:00:04 --:--:--  114k\r100  485k    0     0  100  485k      0  94421  0:00:05  0:00:05 --:--:-- 94433\r100  485k    0     0  100  485k      0  79155  0:00:06  0:00:06 --:--:--     0\r100  485k    0     0  100  485k      0  68138  0:00:07  0:00:07 --:--:--     0\r100  485k    0     0  100  485k      0  59813  0:00:08  0:00:08 --:--:--     0\r100  485k    0     0  100  485k      0  53384  0:00:09  0:00:09 --:--:--     0\r100  485k    0     0  100  485k      0  48150  0:00:10  0:00:10 --:--:--     0< HTTP/1.1 200 OK\r\r\n< Server: Werkzeug/2.3.7 Python/3.10.5\r\r\n< Date: Tue, 14 Nov 2023 07:04:35 GMT\r\r\n< Content-Type: text/html; charset=utf-8\r\r\n< Content-Length: 2578\r\r\n< Connection: close\r\r\n< \r\r\n{ [2578 bytes data]\r\n\r100  487k  100  2578  100  485k    229  44188  0:00:11  0:00:11 --:--:--   519\r100  487k  100  2578  100  485k    229  44188  0:00:11  0:00:11 --:--:--   652\r\n* Closing connection 0\r\n<!doctype html>\n<head>\n    <title>AutoOD: Automatic Outlier Detection</title>\n    <link rel="stylesheet" type="text/css" href="/static/css/style.css"/>\n    <link rel="stylesheet" href="/static/font-awesome-4.7.0/css/font-awesome.min.css">\n    <link rel="stylesheet" type="text/css" href="/static/css/d3_visualization.css"> \n</head>\n<script\n\tsrc="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>\n<!-- DH -->\n<body> \n    <ul>\n        \n        <li id = "nav" class="">\n            <a href="/autood/index">Input Page</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/results_summary">Results Summary</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/result">Result Page</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/index">Rerun</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/about">About</a>\n        </li>\n        \n    </ul>\n</body>\n<!-- DH -->\n\n<script>\n      $(document).ready(function(){\n        var output = document.getElementById(\'output\');\n        var xhr = new XMLHttpRequest();\n        xhr.open(\'GET\', "/running_logs", true);\n        xhr.send();\n        setInterval(function() {\n          output.textContent = xhr.responseText;\n        }, 500);\n      });\n    </script>\n<body>\n<div class="header" style="text-align:center">\n    <h1>AutoOD: Automatic Outlier Detection</h1>\n</div>\n<center>\n    <h3>Detection Results</h3>\n    <form enctype=multipart/form-data>\n        <table>\n            <tr>\n                <td>F-1 of AutoOD</td>\n                <td>0.5344352617079889</td>\n            </tr>\n            <tr>\n                <td>F-1 of Best Unsupervised Detector</td>\n                <td>0.5603864734299517</td>\n            </tr>\n            <tr>\n                <td>Best Unsupervised Detector</td>\n                <td>KNN</td>\n            </tr>\n        </table>\n    </form>\n\n    \n    <h3>Download Final Results:</h3>\n    <table>\n        <tr>\n            <td>Detection Results:</td>\n            <td><a href="/return-files/results_cardio_1699945475.csv"  target="_blank"><i class="fa fa-download" aria-hidden="true"></i>Outlier Results</a></td>\n        </tr>\n    </table>\n    \n\n    \n    <h3>Download Training Log: </h3>\n    <table>\n        <tr>\n            <td>Training Log:</td>\n            <td><a href="/return-files/log_cardio_csv_1699945475" target="_blank"><i class="fa fa-download" aria-hidden="true"></i>Training Log</a></td>\n        </tr>\n    </table>\n    \n\n</center>\n</body>'

    def test_response(self):
        self.assertIsNotNone(self.response)

        # Parses response HTML
        self.parser.feed(str(self.response))
        self.assertIsNotNone(self.parser.parsed_response)
        print("----Verifying correctness of response----")

        i = 0
        num_stylesheets = 0
        for link_batch in self.parser.parsed_response:
            for link in link_batch:
                if link[1] == 'stylesheet':
                    num_stylesheets += 1
                if link[0] == 'href':
                    results_file = '/return-files/results'
                    log_file = '/return-files/log'
                    css_file = '/static/'
                    if link[1][:len(results_file)] == results_file and link[1][:len(css_file)] != css_file:
                        self.links_required['/return-files/*.csv'] = 1
                    elif link[1][:len(log_file)] == log_file and link[1][:len(css_file)] != css_file:
                        self.links_required['/return-files/log*'] = 1
                    elif link[1][:len(css_file)] != css_file:
                        self.links_required[link[1]] = 1
        print(self.links_required)
        # Check that all required links are provided in the response
        self.assertListEqual(list(self.links_required.values()), [1, 1, 1, 1, 1, 1])
        # Check that the correct number of stylesheets is being used
        self.assertEqual(num_stylesheets, 3)


class ResponseParser(HTMLParser):
    parsed_response = []
    def __init__(self):
        HTMLParser.__init__(self)
        self.parsed_response = []

    def handle_starttag(self, tag, attrs):
        if tag == 'link' or tag == 'a':
            self.parsed_response.append(attrs)



# Runs the test suites
if __name__ == '__main__':
    # out = b'  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\r\n                                 Dload  Upload   Total   Spent    Left  Speed\r\n\r  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0*   Trying 127.0.0.1:8080...\r\n* Connected to localhost (127.0.0.1) port 8080 (#0)\r\n> POST /autood/index HTTP/1.1\r\r\n> Host: localhost:8080\r\r\n> User-Agent: curl/8.0.1\r\r\n> Accept: */*\r\r\n> Content-Length: 496817\r\r\n> Content-Type: multipart/form-data; boundary=------------------------f869d27f8c8a1bf7\r\r\n> \r\r\n} [65536 bytes data]\r\n* We are completely uploaded and fine\r\n\r100  485k    0     0  100  485k      0   398k  0:00:01  0:00:01 --:--:--  398k\r100  485k    0     0  100  485k      0   218k  0:00:02  0:00:02 --:--:--  218k\r100  485k    0     0  100  485k      0   149k  0:00:03  0:00:03 --:--:--  150k\r100  485k    0     0  100  485k      0   114k  0:00:04  0:00:04 --:--:--  114k\r100  485k    0     0  100  485k      0  94839  0:00:05  0:00:05 --:--:-- 94848\r100  485k    0     0  100  485k      0  79501  0:00:06  0:00:06 --:--:--     0\r100  485k    0     0  100  485k      0  68463  0:00:07  0:00:07 --:--:--     0\r100  485k    0     0  100  485k      0  60117  0:00:08  0:00:08 --:--:--     0\r100  485k    0     0  100  485k      0  53543  0:00:09  0:00:09 --:--:--     0\r100  485k    0     0  100  485k      0  48265  0:00:10  0:00:10 --:--:--     0\r100  485k    0     0  100  485k      0  43955  0:00:11  0:00:11 --:--:--     0\r100  485k    0     0  100  485k      0  40338  0:00:12  0:00:12 --:--:--     0< HTTP/1.1 200 OK\r\r\n< Server: Werkzeug/2.3.7 Python/3.10.5\r\r\n< Date: Tue, 14 Nov 2023 03:41:58 GMT\r\r\n< Content-Type: text/html; charset=utf-8\r\r\n< Content-Length: 2565\r\r\n< Connection: close\r\r\n< \r\r\n{ [2565 bytes data]\r\n\r100  487k  100  2565  100  485k    206  40039  0:00:12  0:00:12 --:--:--   618\r\n* Closing connection 0\r\n<!doctype html>\n<head>\n    <title>AutoOD: Automatic Outlier Detection</title>\n    <link rel="stylesheet" type="text/css" href="/static/css/style.css"/>\n    <link rel="stylesheet" href="/static/font-awesome-4.7.0/css/font-awesome.min.css">\n    <link rel="stylesheet" type="text/css" href="/static/css/d3_visualization.css"> \n</head>\n<script\n\tsrc="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>\n<!-- DH -->\n<body> \n    <ul>\n        \n        <li id = "nav" class="">\n            <a href="/autood/index">Input Page</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/results_summary">Results Summary</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/result">Result Page</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/index">Rerun</a>\n        </li>\n        \n        <li id = "nav" class="">\n            <a href="/autood/about">About</a>\n        </li>\n        \n    </ul>\n</body>\n<!-- DH -->\n\n<script>\n      $(document).ready(function(){\n        var output = document.getElementById(\'output\');\n        var xhr = new XMLHttpRequest();\n        xhr.open(\'GET\', "/running_logs", true);\n        xhr.send();\n        setInterval(function() {\n          output.textContent = xhr.responseText;\n        }, 500);\n      });\n    </script>\n<body>\n<div class="header" style="text-align:center">\n    <h1>AutoOD: Automatic Outlier Detection</h1>\n</div>\n<center>\n    <h3>Detection Results</h3>\n    <form enctype=multipart/form-data>\n        <table>\n            <tr>\n                <td>F-1 of AutoOD</td>\n                <td>0.332</td>\n            </tr>\n            <tr>\n                <td>F-1 of Best Unsupervised Detector</td>\n                <td>0.3022222222222222</td>\n            </tr>\n            <tr>\n                <td>Best Unsupervised Detector</td>\n                <td>LOF</td>\n            </tr>\n        </table>\n    </form>\n\n    \n    <h3>Download Final Results:</h3>\n    <table>\n        <tr>\n            <td>Detection Results:</td>\n            <td><a href="/return-files/results_cardio_1699933318.csv"  target="_blank"><i class="fa fa-download" aria-hidden="true"></i>Outlier Results</a></td>\n        </tr>\n    </table>\n    \n\n    \n    <h3>Download Training Log: </h3>\n    <table>\n        <tr>\n            <td>Training Log:</td>\n            <td><a href="/return-files/log_cardio_csv_1699933318" target="_blank"><i class="fa fa-download" aria-hidden="true"></i>Training Log</a></td>\n        </tr>\n    </table>\n    \n\n</center>\n</body>'
    # parser = ResponseParser()
    # parser.feed(str(out))
    # print(parser.parsed_response)
    runner = unittest.TextTestRunner()
    runner.run(post_suite())
