import json

from data.repository import DataRepository
from jobs.job_status import JobStatus


repository = DataRepository()


def queue_job(job_type: str, params: dict | None = None):
    repository.queue_job(
        job_type,
        json.dumps(params or {}),
        JobStatus.QUEUED.value,
    )