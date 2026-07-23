from settings import settings


def test_require_auth_in_prod(test_server, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(settings, "local_env", False)

        response = test_server.get("cron")
        assert response.status_code == 401


def test_check_auth_in_prod(test_server, monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(settings, "local_env", False)

        response = test_server.get(
            "cron", headers={"authorization": "Bearer wrong_secret"}
        )
        assert response.status_code == 401

        response = test_server.get(
            "cron", headers={"authorization": f"Bearer {settings.cron_secret}"}
        )
        assert response.status_code == 200
