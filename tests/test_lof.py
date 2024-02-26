import json

from tests.output_processing import process_logs, get_log_file

lof_user_id = '106fae0e-d2f0-4a0a-90f2-9d6034adece4'


def test_lof_default_request(client, cardio_file):
    form = dict(
        file=cardio_file,
        indexColName="id", labelColName="label",
        outlierRangeMin="3", outlierRangeMax="12",
        detectionMethods="lof")
    with client.session_transaction() as session:
        session['user_id'] = lof_user_id  # Test ID in the DB

    post_response = client.post("http://localhost:8080/autood/index",
                                data=form, content_type='multipart/form-data')
    assert post_response.status_code == 302


def test_lof_get_results(client):
    get_response = client.get("http://localhost:8080/autood/result")
    assert get_response.status_code == 200


def test_lof_get_run_count(client):
    with client.session_transaction() as session:
        session['user_id'] = lof_user_id  # Test ID in the DB
    run_count = client.get("http://localhost:8080/getRunCount").get_data()
    assert run_count.decode('utf-8')[0] == '1'                       # Only 1 run


def test_lof_get_results_json(client):
    results_response = client.get(f"http://localhost:8080/data/{lof_user_id}/1")
    assert results_response.status_code == 200
    results_json = results_response.get_data()
    assert len(json.loads(results_json)) == 1831    # num elements in cardio.csv


def test_lof_job_log(client):
    with client.session_transaction() as session:
        session['user_id'] = lof_user_id  # Test ID in the DB
    lof_logs = open(get_log_file("tests\\test_output\\",
                                 lof_user_id,
                                 'cardio.csv', 1), 'r').readlines()
    lof_logs_dict, lof_log_statements = process_logs(lof_logs)
    assert lof_logs_dict is not None
    assert lof_log_statements is not None

    # Check correct inputs and detection method running
    assert lof_logs_dict['Dataset Name'] == 'cardio'
    assert lof_logs_dict['Dataset size'] == '(1831, 21), dataset label size'
    assert lof_logs_dict['Best Unsupervised Outlier Detection Method (post-LOF)'] == "['LOF']"

    # Check DB connection, no errors with DB, and two rounds of training
    assert ['Start running LOF with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], N_range=[54, 87, 120, 153, 186, 219]']\
           in lof_log_statements
    assert ['Start First-round AutoOD training...'] in lof_log_statements
    assert ['Start Second-round AutoOD training...'] in lof_log_statements
    assert ['Error connecting to the database or executing query.'] not in lof_log_statements
    assert ['Instance Index Ranges: [[0, 60]]'] in lof_log_statements
    assert ['Detector Index Ranges: [[0, 10]]'] in lof_log_statements
