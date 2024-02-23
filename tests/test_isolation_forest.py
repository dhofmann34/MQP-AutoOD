import json

from tests.output_processing import process_logs, get_log_file

if_user_id = '01531373-f08f-410e-8275-96d5d8df3621'


def test_if_default_request(client, cardio_file):
    form = dict(
        file=cardio_file,
        indexColName="id", labelColName="label",
        outlierRangeMin="2", outlierRangeMax="10",
        detectionMethods="if")
    with client.session_transaction() as session:
        session['user_id'] = if_user_id  # Test ID in the DB

    post_response = client.post("http://localhost:8080/autood/index",
                                data=form, content_type='multipart/form-data')
    assert post_response.status_code == 302


def test_if_get_results(client):
    get_response = client.get("http://localhost:8080/autood/result")
    assert get_response.status_code == 200


def test_if_get_run_count(client):
    with client.session_transaction() as session:
        session['user_id'] = if_user_id  # Test ID in the DB
    run_count = client.get("http://localhost:8080/getRunCount").get_data()
    assert run_count.decode('utf-8')[0] == '1'                       # Only 1 run


def test_if_get_results_json(client):
    results_response = client.get(f"http://localhost:8080/data/{if_user_id}/1")
    assert results_response.status_code == 200
    results_json = results_response.get_data()
    assert len(json.loads(results_json)) == 1831    # num elements in cardio.csv


def test_if_job_log(client):
    with client.session_transaction() as session:
        session['user_id'] = if_user_id  # Test ID in the DB
    if_logs = open(get_log_file("tests\\test_output\\", if_user_id, 'cardio.csv', 1), 'r').readlines()
    if_logs_dict, if_log_statements = process_logs(if_logs)
    assert if_logs_dict is not None
    assert if_log_statements is not None

    # Check correct inputs and detection method running
    assert if_logs_dict['Dataset Name'] == 'cardio'
    assert if_logs_dict['Dataset size'] == '(1831, 21), dataset label size'
    assert if_logs_dict['Best Unsupervised Outlier Detection Method (post-Isolation Forest)'] == "['Isolation_Forest']"
    assert if_logs_dict['Start running Isolation Forest with max feature'] == '[0.5, 0.6, 0.7, 0.8, 0.9], N_range'

    # Check DB connection, no errors with DB, and two rounds of training
    assert ['Start First-round AutoOD training...'] in if_log_statements
    assert ['Start Second-round AutoOD training...'] in if_log_statements
    assert ['Error connecting to the database or executing query.'] not in if_log_statements
    assert ['Instance Index Ranges: [[0, 30]]'] in if_log_statements
    assert ['Detector Index Ranges: [[0, 5]]'] in if_log_statements
