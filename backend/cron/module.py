from abc import abstractmethod

from datetime import datetime, timedelta
from typing import Annotated, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class CronModule:
    def get_all_cron_jobs(self) -> list[ScheduledCronJob]:
        pass

    def get_active_cron_jobs(self) -> list[ScheduledCronJob]:
        pass


class ScheduledCronJob(BaseModel):
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


class CronJobInterface(BaseModel):
    @abstractmethod
    def execute(self):
        pass


class ExampleCronJob(CronJobInterface):
    job_type: Literal["example_job"]

    def execute(self):
        pass
