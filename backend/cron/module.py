from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Annotated, Literal, LiteralString, Union
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from sqlalchemy import select, update

import database
from database import model


class CronModule:
    def get_all_cron_jobs(self) -> list[CronJob]:
        """Returns all registered cron jobs"""
        session = database.get_session()

        return list(
            map(
                CronJob.model_validate,
                session.execute(select(model.CronJobTable)).scalars().all(),
            )
        )

    def get_queued_cron_jobs(self) -> list[CronJob]:
        """Returns the cron jobs currently queued for the next execution cycle"""
        now = datetime.now()
        return list(
            filter(
                lambda job: job.enabled and (job.last_executed + job.period < now),
                self.get_all_cron_jobs(),
            )
        )

    def patch_cron_job(self, job: CronJob):
        session = database.get_session()
        session.execute(
            update(model.CronJobTable)
            .where(model.CronJobTable.id == job.id)
            .values(**job.model_dump())
        )
        session.commit()


class CronJob(BaseModel):
    # from_attributes allows SQLAlchemy record conversion
    model_config = ConfigDict(from_attributes=True)

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
Update this Union to add new Job types.

Make sure your subclass has class variable `job_type: Literal[discriminant]`
where discriminant is a unique string literal (see ExampleCronJob).
"""


class CronJobInterface(BaseModel):
    @property
    @abstractmethod
    def job_type(self) -> LiteralString:
        pass

    @abstractmethod
    def execute(self):
        pass


class ExampleCronJob(CronJobInterface):
    job_type: Literal["example_job"] = Field(default="example_job")

    def execute(self):
        pass
