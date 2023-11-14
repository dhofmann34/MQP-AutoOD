import unittest
import subprocess

# TODO: change all print statements to log statements

# Test suite of post request tests
def post_suite():
    post_suite = unittest.TestSuite()
    post_suite.addTest(KNNTestCase('test_results'))
    # Each detection method individually
    # 2 of them together
    # all 4 of them
    return post_suite

class KNNTestCase(unittest.TestCase):
    def setUp(self):
        try:
            self.response = subprocess.check_output(
                "curl -F file='@C:\\Users\\tgand\\OneDrive\\Desktop\\WPI Classes\\MQP\\MQP-AutoOD\\files\\cardio.csv' -F indexColName=id -F labelColName=label -F outlierRangeMin=5 -F outlierRangeMax=15 -F detectionMethods=lof -v http://localhost:8080/autood/index",
                timeout=200,
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            self.response = None
            print("Post request with KNN failed to get a response.")

    def test_results(self):
        self.assertNotEqual(self.response, None)
        print(self.response)

    # def tearDown(self):
        # self.response.dispose()

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


# Runs the test suites
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(post_suite())
