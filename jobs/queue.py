import json
from data.raw import get_connection
from jobs.job_status import JobStatus


def queue_job(job_type: str, params: dict = {}):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job (type, arguments, status)
        VALUES (%(job_type)s, %(args)s, %(status)s)
    """, {
        "job_type": job_type,
        "args": json.dumps(params),
        "status": JobStatus.QUEUED.value
    })
    conn.commit()