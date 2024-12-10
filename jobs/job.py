from enum import Enum
import json

from data.raw import get_connection


class JobStatus(Enum):
    NOT_STARTED = 'NOT_STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'


def perform_test_job(**kwargs):
    print(kwargs)
    return True

class Job:
    __types = {
        "test": perform_test_job
    }

    def queue(job_type: str, args: dict):
        if job_type not in Job.__types:
            raise NotImplementedError(f"No registered job type for '{job_type}'")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job (type, arguments, status)
            VALUES (%(job_type)s, %(args)s, %(status)s)
        """, {
            "job_type": job_type,
            "args": json.dumps(args),
            "status": JobStatus.NOT_STARTED.value
        })
        conn.commit()


    def execute_next():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, type, arguments
            FROM job
            WHERE status = %(status)s
            ORDER BY queue_time ASC
            LIMIT 1;
        """, {
            "status": JobStatus.NOT_STARTED.value
        })
        id, job_type, args = cursor.fetchone()

        execute = Job.__types.get(job_type, None)
        if execute is None:
            raise NotImplementedError(f"No registered job type for {job_type}")
        
        try:
            cursor.execute("""
                UPDATE job
                SET (status, start_time) = (SELECT %(status)s, CURRENT_TIMESTAMP)
                WHERE id = %(id)s;
            """, {
                "id": id,
                "status": JobStatus.IN_PROGRESS.value,
            })
            conn.commit()
            result = execute(**json.loads(args))
            cursor.execute("""
                UPDATE job
                SET (status, end_time) = (SELECT %(status)s, CURRENT_TIMESTAMP)
                WHERE id = %(id)s;
            """, {
                "id": id,
                "status": JobStatus.SUCCESS.value if result else JobStatus.FAILURE.value,
            })
            conn.commit()
        except Exception as e:
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
            

if __name__ == '__main__':
    Job.queue('test', {"foo": "bar"})
    Job.execute_next()