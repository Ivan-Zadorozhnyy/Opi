from main import app
import json

def test_create_report_configuration():
    with app.test_client() as client:
        response = client.post('/api/report/weeklyActivity',
                               data=json.dumps({
                                   "metrics": ["dailyAverage"],
                                   "users": ["d580539f-9ee8-4300-b48e-0e8d0810f766"]
                               }),
                               content_type='application/json')

        assert response.status_code == 200
        assert response.get_json() == {}

def test_retrieve_non_existent_report():
    with app.test_client() as client:
        response = client.get('/api/report/nonExistentReport?from=2023-10-01&to=2023-10-15')
        assert response.status_code == 404
        assert response.get_json() == {"error": "Report not found."}
