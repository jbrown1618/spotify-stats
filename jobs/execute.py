import json

from data.repository import DataRepository
from jobs.job_status import JobStatus
from jobs.job_types import job_types


repository = DataRepository()


def execute_next_job() -> bool:
    next_job = repository.next_queued_job(JobStatus.QUEUED.value)
    if next_job is None:
        return False

    print(
        f"Executing job {next_job.id}: {next_job.type} "
        f"with {next_job.arguments}"
    )

    execute = job_types.get(next_job.type, None)
    if execute is None:
        message = f"No registered job type for {next_job.type}"
        print("Job failed", message)
        repository.mark_job_failed(
            next_job.id,
            JobStatus.FAILURE.value,
            message,
        )
        return True

    try:
        repository.mark_job_started(
            next_job.id,
            JobStatus.IN_PROGRESS.value,
        )
        execute(**json.loads(next_job.arguments))
        repository.mark_job_succeeded(
            next_job.id,
            JobStatus.SUCCESS.value,
        )
    except Exception as error:
        print("Job failed", str(error))
        repository.mark_job_failed(
            next_job.id,
            JobStatus.FAILURE.value,
            str(error),
        )

    return True
