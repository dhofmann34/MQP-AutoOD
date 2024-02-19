import json

from tests.output_processing import process_logs, get_log_file

all_user_id = '0eb957c1-1aea-457a-8935-6fb26230da8f'


def test_all_default_request(client, cardio_file):
    form = dict(
        file=cardio_file,
        indexColName="id", labelColName="label",
        outlierRangeMin="5", outlierRangeMax="15",
        detectionMethods=["knn", "lof", "if", "mahala"])
    with client.session_transaction() as session:
        session['user_id'] = all_user_id  # Test ID in the DB

    post_response = client.post("http://localhost:8080/autood/index",
                                data=form, content_type='multipart/form-data')
    assert post_response.status_code == 302


def test_all_get_results(client):
    get_response = client.get("http://localhost:8080/autood/result")
    assert get_response.status_code == 200


def test_all_get_run_count(client):
    with client.session_transaction() as session:
        session['user_id'] = all_user_id  # Test ID in the DB
    run_count = client.get("http://localhost:8080/getRunCount").get_data()
    assert run_count.decode('utf-8')[0] == '1'                       # Only 1 run


def test_all_get_results_json(client):
    results_response = client.get(f"http://localhost:8080/data/{all_user_id}/1")
    assert results_response.status_code == 200
    results_json = results_response.get_data()
    assert len(json.loads(results_json)) == 1831    # num elements in cardio.csv


def test_all_job_log(client):
    with client.session_transaction() as session:
        session['user_id'] = all_user_id  # Test ID in the DB
    all_logs = open(get_log_file("tests\\test_output\\",
                                 all_user_id,
                                 'cardio.csv', 1), 'r').readlines()
    all_logs_dict, all_log_statements = process_logs(all_logs)
    assert all_logs_dict is not None
    assert all_log_statements is not None

    # Check correct inputs and detection method running
    assert all_logs_dict['Dataset Name'] == 'cardio'
    assert all_logs_dict['Dataset size'] == '(1831, 21), dataset label size'
    assert all_logs_dict['Start running Isolation Forest with max feature'] == '[0.5, 0.6, 0.7, 0.8, 0.9], N_range'
    assert all_logs_dict['Best Unsupervised Outlier Detection Method (post-KNN)'] == "['KNN']"
    assert all_logs_dict['Best Unsupervised Outlier Detection Method (post-LOF)'] == "['LOF']"
    assert all_logs_dict['Best Unsupervised Outlier Detection Method (post-Isolation Forest)'] == "['Isolation_Forest']"
    assert all_logs_dict['Best Unsupervised Outlier Detection Method (post-Mahalanobis)'] == "['Isolation_Forest']"

    # Check DB connection, no errors with DB, and two rounds of training
    assert ['Start running KNN with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], N_range=[91, 128, 164, 201, 238, 274]']\
           in all_log_statements
    assert ['Start running LOF with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], N_range=[91, 128, 164, 201, 238, 274]']\
           in all_log_statements
    assert ['Start running Mahalanobis..']\
           in all_log_statements
    assert ['Start First-round AutoOD training...'] in all_log_statements
    assert ['Start Second-round AutoOD training...'] in all_log_statements
    assert ['Error connecting to the database or executing query.'] not in all_log_statements
    assert ['Instance Index Ranges: [[0, 60], [60, 120], [120, 150], [150, 156]]'] in all_log_statements
    assert ['Detector Index Ranges: [[0, 10], [10, 20], [20, 25], [25, 26]]'] in all_log_statements
