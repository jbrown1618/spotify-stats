from data.raw import get_connection
from jobs.job_status import JobStatus


def expire_stale_jobs():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE job
            SET
                status = %(failure_status)s,
                error = 'Job expired after remaining in progress for more than one hour',
                end_time = CURRENT_TIMESTAMP
            WHERE status = %(in_progress_status)s
                AND start_time < CURRENT_TIMESTAMP - INTERVAL '1 hour';
            """,
            {
                "failure_status": JobStatus.FAILURE.value,
                "in_progress_status": JobStatus.IN_PROGRESS.value,
            },
        )
        expired_count = cursor.rowcount
        conn.commit()

    print(f"Expired {expired_count} stale jobs", flush=True)


if __name__ == '__main__':
    expire_stale_jobs()