from fastapi.testclient import TestClient


def test_notify_managers_new_application(test_server: TestClient, default_database):
    """Test that managers get notified when a new application is submitted"""
    response = test_server.post("/notifications/notify-managers-new-application", json={
        "email": "applicant@example.com",
        "name": "John Doe"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Managers notified successfully."


def test_notify_applicant_approved(test_server: TestClient):
    """Test that applicant gets notified when approved"""
    response = test_server.post("/notifications/notify-applicant-approved", json={
        "email": "applicant@example.com",
        "name": "John Doe"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Applicant notified of approval."


def test_notify_applicant_denied(test_server: TestClient):
    """Test that applicant gets notified when denied"""
    response = test_server.post("/notifications/notify-applicant-denied", json={
        "email": "applicant@example.com",
        "name": "John Doe"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Applicant notified of denial."


def test_notify_applicant_revision_requested(test_server: TestClient):
    """Test that applicant gets notified when revision is requested"""
    response = test_server.post("/notifications/notify-applicant-revision", json={
        "email": "applicant@example.com",
        "name": "John Doe",
        "notes": "Please provide more details about your research interests."
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Applicant notified of revision request."


def test_notify_membership_status(test_server: TestClient):
    """Test that member gets notified of status change"""
    response = test_server.post("/notifications/notify-membership-status", json={
        "email": "member@example.com",
        "name": "Jane Doe",
        "status": "active"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Membership status notification sent."


def test_send_email_to_all_members(test_server: TestClient):
    """Test that manager can send email to all members"""
    response = test_server.post("/notifications/send-all-members", json={
        "subject": "Important Announcement",
        "content": "This is a test announcement to all members."
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Email sent to all members successfully."