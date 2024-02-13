import json

from tests.output_processing import process_logs, get_log_file

rerun_user_id = '13bc99cc-5c41-409d-b7c2-ba5fb72f0fed'


def test_rerun_all_request(client, cardio_file):
    form = dict(
        file=cardio_file,
        indexColName="id", labelColName="label",
        outlierRangeMin="5", outlierRangeMax="15",
        detectionMethods=["knn", "lof", "if", "mahala"])
    settings = {"lofKRange": "[10,20,30,40]", "knnKRange": "[15,25,35]", "ifRange": "[0.2,0.3,0.4,1.0]",
                "runMahalanobis": "true", "globalMinOutlier": 2, "globalMaxOutlier": 10}
    with client.session_transaction() as session:
        session['user_id'] = rerun_user_id  # Test ID in the DB
        session['tab_index'] = 1

    first_run = client.post("http://localhost:8080/autood/index",
                            data=form, content_type='multipart/form-data')
    assert first_run.status_code == 302
    post_response = client.post("http://localhost:8080/autood/result",
                                json=settings, content_type='application/json')
    assert post_response.status_code == 200


def test_rerun_get_results(client):
    get_response = client.get("http://localhost:8080/autood/result")
    assert get_response.status_code == 200


def test_rerun_get_run_count(client):
    with client.session_transaction() as session:
        session['user_id'] = rerun_user_id  # Test ID in the DB
    run_count = client.get("http://localhost:8080/getRunCount").get_data()
    assert run_count.decode('utf-8')[0] == '2'


def test_rerun_get_results_json(client):
    results_response = client.get(f"http://localhost:8080/data/{rerun_user_id}/1")
    assert results_response.status_code == 200
    results_json = results_response.get_data()
    assert len(json.loads(results_json)) == 1831    # num elements in cardio.csv

    results_response_2 = client.get(f"http://localhost:8080/data/{rerun_user_id}/2")
    assert results_response.status_code == 200
    results_json_2 = results_response_2.get_data()
    assert len(json.loads(results_json_2)) == 1831


def test_rerun_job_log(client):
    with client.session_transaction() as session:
        session['user_id'] = rerun_user_id  # Test ID in the DB
    rerun_logs = open(get_log_file("tests\\test_output\\",
                                   rerun_user_id, 'cardio', 2), 'r').readlines()
    rerun_logs_dict, rerun_log_statements = process_logs(rerun_logs)
    assert rerun_logs_dict is not None
    assert rerun_log_statements is not None

    # Check correct inputs and detection method running
    assert rerun_logs_dict['selected methods'] == "[<OutlierDetectionMethod.LOF: 1>, <OutlierDetectionMethod.KNN: 2>, " \
                                                  "<OutlierDetectionMethod.IsolationForest: 3>, " \
                                                  "<OutlierDetectionMethod.Mahalanobis: 4>]"
    assert rerun_logs_dict['Dataset Name'] == 'cardio'
    assert rerun_logs_dict['Dataset size'] == '(1831, 21), dataset label size'
    assert rerun_logs_dict['Start running Isolation Forest with max feature'] == '[0.2, 0.3, 0.4, 1.0], N_range'
    assert rerun_logs_dict['Best Unsupervised Outlier Detection Method (post-KNN)'] == "['KNN']"
    assert rerun_logs_dict['Best Unsupervised Outlier Detection Method (post-LOF)'] == "['LOF']"
    assert rerun_logs_dict['Best Unsupervised Outlier Detection Method (post-Isolation Forest)'] == "['Isolation_Forest']"
    assert rerun_logs_dict['Best Unsupervised Outlier Detection Method (post-Mahalanobis)'] == "['Isolation_Forest']"

    # Check DB connection, no errors with DB, and two rounds of training
    assert ['Start running KNN with k=[15, 25, 35], N_range=[36, 65, 95, 124, 153, 183]']\
           in rerun_log_statements
    assert ['Start running LOF with k=[10, 20, 30, 40], N_range=[36, 65, 95, 124, 153, 183]']\
           in rerun_log_statements
    assert ['Start running Mahalanobis..']\
           in rerun_log_statements
    assert ['Start First-round AutoOD training...'] in rerun_log_statements
    assert ['Start Second-round AutoOD training...'] in rerun_log_statements
    assert ['Error connecting to the database or executing query.'] not in rerun_log_statements
    assert ['Instance Index Ranges: [[0, 24], [24, 42], [42, 66], [66, 72]]'] in rerun_log_statements
    assert ['Detector Index Ranges: [[0, 4], [4, 7], [7, 11], [11, 12]]'] in rerun_log_statements
