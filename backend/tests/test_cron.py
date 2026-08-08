from datetime import datetime
from typing import Callable

from sqlalchemy.orm import Session

from cron.module import CronModule, ExampleCronJob, CronJob
from settings import SETTINGS
import database.model as model


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


def test_conversion():
    job = model.CronJobTable(
        id=1,
        enabled=False,
        last_executed=datetime(2026, 1, 1),
        period=60 * 60 * 24,
        job={"job_type": "example_job"},
    )

    converted_job = CronJob.model_validate_sqlalchemy(job)

    assert isinstance(converted_job.job, ExampleCronJob)

    round_trip = model.CronJobTable(**converted_job.model_dump())

    assert round_trip.job == {"job_type": "example_job"}


def test_queued(test_server, mock_get_session: Callable[[], Session]):
    session: Session = mock_get_session()
    session.add(
        model.CronJobTable(
            id=1,
            enabled=False,
            last_executed=datetime(2026, 1, 1),
            period=60 * 60 * 24,
            job={"job_type": "example_job"},
        )
    )
    session.commit()

    r = test_server.get("cron/jobs")
    assert r.status_code == 200
    r = r.json()
    assert r == [
        {
            "id": 1,
            "enabled": False,
            "last_executed": "2026-01-01T00:00:00",
            "period": 86400,
            "job": {"job_type": "example_job"},
        }
    ]


def test_execute_cron(test_server, mock_get_session: Callable[[], Session]):
    session: Session = mock_get_session()
    session.add(
        model.CronJobTable(
            id=1,
            enabled=True,
            last_executed=datetime(2026, 1, 1),
            period=60 * 60 * 24,
            job={"job_type": "example_job"},
        )
    )
    session.commit()

    assert len(CronModule().get_queued_cron_jobs()) == 1

    r = test_server.get("cron")
    assert r.status_code == 200

    assert len(CronModule().get_queued_cron_jobs()) == 0

    r = test_server.get("cron/jobs")
    assert r.status_code == 200
    job = r.json()[0]
    assert job == {
        "id": 1,
        "enabled": True,
        "last_executed": job["last_executed"],
        "period": 86400,
        "job": {"job_type": "example_job"},
    }
