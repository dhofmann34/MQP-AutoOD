import json

from tests.output_processing import process_logs, get_log_file

mahalanobis_user_id = '0cf6108a-6f56-4c9d-8bda-90b72cc058c3'


def test_mahala_default_request(client, cardio_file):
    form = dict(
        file=cardio_file,
        indexColName="id", labelColName="label",
        outlierRangeMin="3", outlierRangeMax="12",
        detectionMethods="mahala")
    with client.session_transaction() as session:
        session['user_id'] = mahalanobis_user_id  # Test ID in the DB

    post_response = client.post("http://localhost:8080/autood/index",
                                data=form, content_type='multipart/form-data')
    assert post_response.status_code == 302


def test_mahala_get_results(client):
    get_response = client.get("http://localhost:8080/autood/result")
    assert get_response.status_code == 200


def test_mahala_get_run_count(client):
    with client.session_transaction() as session:
        session['user_id'] = mahalanobis_user_id  # Test ID in the DB
    run_count = client.get("http://localhost:8080/getRunCount").get_data()
    assert run_count.decode('utf-8')[0] == '1'                       # Only 1 run


def test_mahala_get_results_json(client):
    results_response = client.get(f"http://localhost:8080/data/{mahalanobis_user_id}/1")
    assert results_response.status_code == 200
    results_json = results_response.get_data()
    assert len(json.loads(results_json)) == 1831    # num elements in cardio.csv


def test_mahala_job_log(client):
    with client.session_transaction() as session:
        session['user_id'] = mahalanobis_user_id  # Test ID in the DB
    mahala_logs = open(get_log_file("tests\\test_output\\", mahalanobis_user_id, 'cardio.csv', 1), 'r').readlines()
    mahala_logs_dict, mahala_log_statements = process_logs(mahala_logs)
    assert mahala_logs_dict is not None
    assert mahala_log_statements is not None

    # Check correct inputs and detection method running
    assert mahala_logs_dict['Dataset Name'] == 'cardio'
    assert mahala_logs_dict['Dataset size'] == '(1831, 21), dataset label size'
    assert mahala_logs_dict['Best Unsupervised Outlier Detection Method (post-Mahalanobis)'] == "['mahalanobis']"

    # Check DB connection, no errors with DB, and two rounds of training
    assert ['Start running Mahalanobis..']\
           in mahala_log_statements
    assert ['Start First-round AutoOD training...'] in mahala_log_statements
    assert ['Start Second-round AutoOD training...'] in mahala_log_statements
    assert ['Error connecting to the database or executing query.'] not in mahala_log_statements
    assert ['Instance Index Ranges: [[0, 6]]'] in mahala_log_statements
    assert ['Detector Index Ranges: [[0, 1]]'] in mahala_log_statements
