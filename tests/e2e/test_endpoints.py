import requests

BASE_URL = "http://127.0.0.1:5000"

def test_full_report_flow():
    # Create the report configuration
    resp = requests.post(f"{BASE_URL}/api/report/weeklyActivity", json={
        "metrics": ["dailyAverage", "total", "weeklyAverage"],
        "users": ["d580539f-9ee8-4300-b48e-0e8d0810f766", "b82ac857-bdd3-4ef4-97fa-cef910d9b584"]
    })
    assert resp.status_code == 200
    assert resp.json() == {}

    # Retrieve the report
    resp = requests.get(f"{BASE_URL}/api/report/weeklyActivity?from=2023-10-01&to=2023-10-15")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert any(d['userId'] == "d580539f-9ee8-4300-b48e-0e8d0810f766" for d in data)
    assert any(d['userId'] == "b82ac857-bdd3-4ef4-97fa-cef910d9b584" for d in data)
