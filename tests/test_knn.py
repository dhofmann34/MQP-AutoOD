import json

from tests.output_processing import process_logs, get_log_file


def test_knn_default_request(client, cardio_file):
    form = dict(
        file=cardio_file,
        indexColName="id", labelColName="label",
        outlierRangeMin="5", outlierRangeMax="15",
        detectionMethods="knn")
    with client.session_transaction() as session:
        session['user_id'] = '40508fa7-2b6f-4629-8187-77fe6c541333'  # Test ID in the DB

    post_response = client.post("http://localhost:8080/autood/index",
                                data=form, content_type='multipart/form-data')
    assert post_response.status_code == 302


def test_knn_get_results(client):
    get_response = client.get("http://localhost:8080/autood/result")
    assert get_response.status_code == 200


def test_knn_get_run_count(client):
    with client.session_transaction() as session:
        session['user_id'] = '40508fa7-2b6f-4629-8187-77fe6c541333'  # Test ID in the DB
    run_count = client.get("http://localhost:8080/getRunCount").get_data()
    assert run_count.decode('utf-8')[0] == '1'                       # Only 1 run


def test_knn_get_results_json(client):
    results_response = client.get("http://localhost:8080/data/40508fa7-2b6f-4629-8187-77fe6c541333/1")
    assert results_response.status_code == 200
    results_json = results_response.get_data()
    assert len(json.loads(results_json)) == 1831    # num elements in cardio.csv


def test_knn_job_log(client):
    with client.session_transaction() as session:
        session['user_id'] = '40508fa7-2b6f-4629-8187-77fe6c541333'  # Test ID in the DB
    knn_logs = open(get_log_file("tests\\test_output\\",
                                 '40508fa7-2b6f-4629-8187-77fe6c541333',
                                 'cardio', 1), 'r').readlines()
    knn_logs_dict, knn_log_statements = process_logs(knn_logs)
    assert knn_logs_dict is not None
    assert knn_log_statements is not None
    print(knn_log_statements)

    # Check correct inputs and detection method running
    assert knn_logs_dict['selected methods'] == "['knn']"
    assert knn_logs_dict['Dataset Name'] == 'cardio'
    assert knn_logs_dict['Dataset size'] == '(1831, 21), dataset label size'
    assert knn_logs_dict['Parameters: outlier_percentage_min'] == '5.0%, outlier_percentage_max'
    assert knn_logs_dict['Best Unsupervised Outlier Detection Method (post-KNN)'] == "['KNN']"

    # Check DB connection, no errors with DB, and two rounds of training
    assert ['Start running KNN with k=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], N_range=[91, 128, 164, 201, 238, 274]']\
           in knn_log_statements
    assert ['Start First-round AutoOD training...'] in knn_log_statements
    assert ['Start Second-round AutoOD training...'] in knn_log_statements
    assert ['Error connecting to the database or executing query.'] not in knn_log_statements
    assert ['Instance Index Ranges: [[0, 60]]'] in knn_log_statements
    assert ['Detector Index Ranges: [[0, 10]]'] in knn_log_statements
