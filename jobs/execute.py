import json

from data.raw import get_connection
from jobs.job_types import job_types
from jobs.job_status import JobStatus


def execute_next_job() -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, type, arguments
            FROM job
            WHERE status = %(status)s
            ORDER BY queue_time ASC
            LIMIT 1;
        """, {
            "status": JobStatus.QUEUED.value
        })
        next_job = cursor.fetchone()
        if next_job is None:
            return False
        
        id, job_type, args = next_job
        print(f"Executing job {id}: {job_type} with {args}")

        execute = job_types.get(job_type, None)
        if execute is None:
            message = f"No registered job type for {job_type}"
            print("Job failed", message)
            cursor.execute("""
                UPDATE job
                SET (status, error, end_time) = (SELECT %(status)s, %(err)s, CURRENT_TIMESTAMP)
                WHERE id = %(id)s;
            """, {
                "id": id,
                "status": JobStatus.FAILURE.value,
                "err": message
            })
            conn.commit()
            return True
        
        try:
            cursor.execute("""
                UPDATE job
                SET (status, start_time) = (SELECT %(status)s, CURRENT_TIMESTAMP)
                WHERE id = %(id)s;
            """, {
                "id": id,
                "status": JobStatus.IN_PROGRESS.value
            })
            conn.commit()
            execute(**json.loads(args))
            cursor.execute("""
                UPDATE job
                SET (status, end_time) = (SELECT %(status)s, CURRENT_TIMESTAMP)
                WHERE id = %(id)s;
            """, {
                "id": id,
                "status": JobStatus.SUCCESS.value
            })
            conn.commit()
        except Exception as e:
            print("Job failed", str(e))
            cursor.execute("""
                UPDATE job
                SET (status, error, end_time) = (SELECT %(status)s, %(err)s, CURRENT_TIMESTAMP)
                WHERE id = %(id)s;
            """, {
                "id": id,
                "status": JobStatus.FAILURE.value,
                "err": str(e)
            })
            conn.commit()

    return True
