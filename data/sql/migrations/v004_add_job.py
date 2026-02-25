from data.sql.migrations.migration import Migration
import sqlalchemy

remove_job_table = """
DROP TABLE IF EXISTS job;
"""

add_job_table = """
CREATE TABLE IF NOT EXISTS job (
    id SERIAL PRIMARY KEY,
    type TEXT NOT NULL,
    arguments TEXT NOT NULL,
    status TEXT DEFAULT 'QUEUED',
    error TEXT,
    queue_time timestamp DEFAULT current_timestamp,
    start_time timestamp,
    end_time timestamp
);
"""

class AddJobTable(Migration):
    def __init__(self):
        super().__init__("v4")


    def migrate(self, conn):
        conn.execute(sqlalchemy.text(remove_job_table))
        conn.execute(sqlalchemy.text(add_job_table))


    def reverse(self, conn):
        conn.execute(sqlalchemy.text(remove_job_table))


if __name__ == '__main__':
    AddJobTable().reverse_migration()
    AddJobTable().perform_migration()
