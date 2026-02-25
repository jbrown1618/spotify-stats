import json

import sqlalchemy
from data.raw import get_engine
from jobs.job_types import job_types
from jobs.job_status import JobStatus


def execute_next_job() -> bool:
    with get_engine().connect() as conn:
        result = conn.execute(sqlalchemy.text("""
            SELECT id, type, arguments
            FROM job
            WHERE status = :status
            ORDER BY queue_time ASC
            LIMIT 1;
        """), {
            "status": JobStatus.QUEUED.value
        })
        next_job = result.fetchone()
        if next_job is None:
            return False
        
        id, job_type, args = next_job
        print(f"Executing job {id}: {job_type} with {args}")

        execute = job_types.get(job_type, None)
        if execute is None:
            message = f"No registered job type for {job_type}"
            print("Job failed", message)
            conn.execute(sqlalchemy.text("""
                UPDATE job
                SET (status, error, end_time) = (SELECT :status, :err, CURRENT_TIMESTAMP)
                WHERE id = :id;
            """), {
                "id": id,
                "status": JobStatus.FAILURE.value,
                "err": message
            })
            conn.commit()
            return True
        
        try:
            conn.execute(sqlalchemy.text("""
                UPDATE job
                SET (status, start_time) = (SELECT :status, CURRENT_TIMESTAMP)
                WHERE id = :id;
            """), {
                "id": id,
                "status": JobStatus.IN_PROGRESS.value
            })
            conn.commit()
            execute(**json.loads(args))
            conn.execute(sqlalchemy.text("""
                UPDATE job
                SET (status, end_time) = (SELECT :status, CURRENT_TIMESTAMP)
                WHERE id = :id;
            """), {
                "id": id,
                "status": JobStatus.SUCCESS.value
            })
            conn.commit()
        except Exception as e:
            print("Job failed", str(e))
            conn.execute(sqlalchemy.text("""
                UPDATE job
                SET (status, error, end_time) = (SELECT :status, :err, CURRENT_TIMESTAMP)
                WHERE id = :id;
            """), {
                "id": id,
                "status": JobStatus.FAILURE.value,
                "err": str(e)
            })
            conn.commit()

    return True
