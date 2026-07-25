from datetime import datetime

from cron.module import ExampleCronJob, ScheduledCronJob
from settings import settings
import database.model as model


def test_require_auth_in_prod(test_server, monkeypatch):
    with monkeypatch.context() as m:
        # The Cron endpoint doesn't check authentication locally
        m.setattr(settings, "local_deployment", False)

        response = test_server.get("cron")
        assert response.status_code == 401


def test_check_auth_in_prod(test_server, monkeypatch):
    with monkeypatch.context() as m:
        # The Cron endpoint doesn't check authentication locally
        m.setattr(settings, "local_deployment", False)

        response = test_server.get(
            "cron", headers={"authorization": "Bearer wrong_secret"}
        )
        assert response.status_code == 401

        response = test_server.get(
            "cron", headers={"authorization": f"Bearer {settings.cron_secret}"}
        )
        assert response.status_code == 200


def test_conversion():
    job = model.CronJob(
        id=1,
        enabled=False,
        last_executed=datetime(2026, 1, 1),
        period=60 * 60 * 24,
        job={"job_type": "example_job"},
    )

    converted_job = ScheduledCronJob.model_validate(job)

    assert isinstance(converted_job.job, ExampleCronJob)

    round_trip = model.CronJob(**converted_job.model_dump())

    assert round_trip.job == {"job_type": "example_job"}
