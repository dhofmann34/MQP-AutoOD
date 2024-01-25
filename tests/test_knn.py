
def test_knn_default_request(client, cardio_file):
    form = dict(
        file=cardio_file,
        indexColName="id", labelColName="label",
        outlierRangeMin="5", outlierRangeMax="15",
        detectionMethods="knn")
    response = client.post("http://localhost:8080/autood/index", data=form,
                           content_type='multipart/form-data')
    assert response.status_code == 200
