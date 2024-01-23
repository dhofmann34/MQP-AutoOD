
def test_knn_default_request(client):
    form = {"file": "\\test_files\\cardio.csv",
            "indexColName": "id", "labelColName": "label",
            "outlierRangeMin": "5", "outlierRangeMax": "15", "detectionMethods": "knn"}
    response = client.post("autood/index", data=form)
    assert response.status_code == 200
