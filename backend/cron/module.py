from abc import abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal, Union
from pydantic import Field, field_serializer, field_validator
from sqlalchemy import select, update
from utils import BaseModel

import database
from database import model


class CronModule:
    def get_all_cron_jobs(self) -> list[CronJob]:
        """Returns all registered cron jobs"""
        with database.get_session() as session:
            return list(
                map(
                    CronJob.model_validate_sqlalchemy,
                    session.execute(select(model.CronJobTable)).scalars().all(),
                )
            )

    def get_queued_cron_jobs(self) -> list[CronJob]:
        """Returns the cron jobs currently queued for the next execution cycle"""
        now = datetime.now(timezone.utc)
        return list(
            filter(
                lambda job: job.enabled and (job.last_executed + job.period < now),
                self.get_all_cron_jobs(),
            )
        )

    def patch_cron_job(self, job: CronJob):
        with database.get_session() as session:
            session.execute(
                update(model.CronJobTable)
                .where(model.CronJobTable.id == job.id)
                .values(**job.model_dump())
            )
            session.commit()


class CronJob(BaseModel):
    id: int
    enabled: bool
    last_executed: datetime
    period: timedelta
    job: CronJobTypes

    @field_validator("period", mode="plain")
    @classmethod
    def from_secs(cls, value: int) -> timedelta:
        return timedelta(seconds=value)

    @field_serializer("period")
    def to_secs(self, value: timedelta) -> int:
        return int(value.total_seconds())


type CronJobTypes = Annotated[Union[ExampleCronJob], Field(discriminator="job_type")]
"""
Update this Union to add new Job types. Make sure all members implement CronJobInterface

Make sure your subclass has class variable `job_type: Literal[discriminant]`
where discriminant is a unique string literal (see ExampleCronJob).
"""


class CronJobInterface(BaseModel):
    @abstractmethod
    def execute(self):
        pass


class ExampleCronJob(CronJobInterface):
    job_type: Literal["example_job"] = Field(default="example_job")

    def execute(self):
        pass
