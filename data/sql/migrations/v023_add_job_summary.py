from data.sql.migrations.migration import Migration


add_job_summary = """
ALTER TABLE job
ADD COLUMN IF NOT EXISTS summary JSONB NOT NULL DEFAULT '{}'::JSONB;
"""

remove_job_summary = """
ALTER TABLE job
DROP COLUMN IF EXISTS summary;
"""


class AddJobSummary(Migration):
    def __init__(self):
        super().__init__("v23")

    def migrate(self, cursor):
        cursor.execute(add_job_summary)

    def reverse(self, cursor):
        cursor.execute(remove_job_summary)


if __name__ == "__main__":
    AddJobSummary().perform_migration()
