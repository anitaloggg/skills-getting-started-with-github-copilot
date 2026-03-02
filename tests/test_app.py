from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "tester@example.com"

    # record original list
    orig = list(activities[activity]["participants"])
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Signed up {email}" in resp.json()["message"]

    # now participant appears
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert f"Unregistered {email}" in resp.json()["message"]

    # removing again yields 404
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 404

    # restore original state just in case
    activities[activity]["participants"] = orig


def test_duplicate_signup():
    activity = "Chess Club"
    email = "dup@example.com"

    # sign up twice
    client.post(f"/activities/{activity}/signup", params={"email": email})
    client.post(f"/activities/{activity}/signup", params={"email": email})
    resp = client.get("/activities")
    parts = resp.json()[activity]["participants"]
    assert parts.count(email) == 2

    # cleanup
    activities[activity]["participants"] = [p for p in activities[activity]["participants"] if p != email]
