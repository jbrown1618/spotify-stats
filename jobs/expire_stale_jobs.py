from data.repository import DataRepository
from jobs.job_status import JobStatus


repository = DataRepository()


def expire_stale_jobs():
    expired_count = repository.expire_stale_jobs(
        JobStatus.FAILURE.value,
        JobStatus.IN_PROGRESS.value,
    )
    print(f"Expired {expired_count} stale jobs", flush=True)


if __name__ == '__main__':
    expire_stale_jobs()