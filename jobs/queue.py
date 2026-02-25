import json

import sqlalchemy
from data.raw import get_engine
from jobs.job_status import JobStatus


def queue_job(job_type: str, params: dict = {}):
    with get_engine().begin() as conn:
        conn.execute(sqlalchemy.text("""
            INSERT INTO job (type, arguments, status)
            VALUES (:job_type, :args, :status)
        """), {
            "job_type": job_type,
            "args": json.dumps(params),
            "status": JobStatus.QUEUED.value
        })