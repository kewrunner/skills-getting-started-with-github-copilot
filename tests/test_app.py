from copy import deepcopy

from fastapi.testclient import TestClient
import pytest

from src.app import activities, app


@pytest.fixture
def client():
    original = deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original)


def test_get_activities_returns_seed_data(client):
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_new_participant(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    # Act
    response = client.post("/activities/Unknown Activity/signup?email=student@example.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
