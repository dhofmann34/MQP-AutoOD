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

def test_knn_get_results_json(client):
    results_json = client.get("http://localhost:8080/data/")
    assert results_json is not None
