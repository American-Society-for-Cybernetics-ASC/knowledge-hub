import datetime
from typing import Iterable

import pytest

from database.types import CronJobType
from settings import SETTINGS


class MockData:
    calls: list[CronJobType] = []


@pytest.fixture()
def mock_cron_job(monkeypatch):
    data = MockData()

    def mock_job_list() -> Iterable[str]:
        return [CronJobType.DUES_REMINDERS]

    def mock_period(_job_type: CronJobType):
        return datetime.timedelta(days=1)

    def mock_enabled(job_type: CronJobType):
        return True

    def mock_run(session, job_type: CronJobType):
        data.calls.append(job_type)
        return

    with monkeypatch.context() as m:
        m.setattr("cron.cron_module._job_list", mock_job_list)
        m.setattr("cron.cron_module.handle_get_cron_job_period", mock_period)
        m.setattr("cron.cron_module.handle_get_cron_job_enabled", mock_enabled)
        m.setattr("cron.cron_module.handle_run_cron_job", mock_run)
        yield data


def test_require_auth_in_prod(test_server, monkeypatch):
    with monkeypatch.context() as m:
        # The Cron endpoint doesn't check authentication locally
        m.setattr(SETTINGS, "local_deployment", False)

        response = test_server.get("cron")
        assert response.status_code == 401


def test_check_auth_in_prod(test_server, monkeypatch):
    with monkeypatch.context() as m:
        # The Cron endpoint doesn't check authentication locally
        m.setattr(SETTINGS, "local_deployment", False)

        response = test_server.get(
            "cron", headers={"authorization": "Bearer wrong_secret"}
        )
        assert response.status_code == 401

        response = test_server.get(
            "cron", headers={"authorization": f"Bearer {SETTINGS.cron_secret}"}
        )
        assert response.status_code == 200


def test_execute_cron(test_server, monkeypatch, mock_cron_job):
    # Call job
    r = test_server.get("cron")
    assert r.status_code == 200
    assert len(mock_cron_job.calls) == 1

    # Don't call job again before the period expires
    r = test_server.get("cron")
    assert r.status_code == 200
    assert len(mock_cron_job.calls) == 1

    # Call again in 12 hours
    with monkeypatch.context() as m:
        m.setattr(
            "cron.cron_module._now",
            lambda: (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=12)
            ),
        )

        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_cron_job.calls) == 1

    # Call again in 23 hours
    # (Vercel doesn't promise precise cron jobs to hobby plans, so we DO want this to count as a day!)
    with monkeypatch.context() as m:
        m.setattr(
            "cron.cron_module._now",
            lambda: (
                datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=23)
            ),
        )

        r = test_server.get("cron")
        assert r.status_code == 200
        assert len(mock_cron_job.calls) == 2
