from data.sql.migrations.migration import Migration

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


    def migrate(self, cursor):
        cursor.execute(remove_job_table)
        cursor.execute(add_job_table)


    def reverse(self, cursor):
        cursor.execute(remove_job_table)


if __name__ == '__main__':
    AddJobTable().reverse_migration()
    AddJobTable().perform_migration()