import json
import sys

from jobs.queue import queue_job

job_name = sys.argv[1]
params = {}
if len(sys.argv) > 2:
    params = json.loads(sys.argv[2])

queue_job(job_name, params)