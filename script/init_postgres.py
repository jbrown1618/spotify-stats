import psycopg2

from utils.settings import postgres_host, postgres_password, postgres_port, postgres_user

conn = psycopg2.connect(database="spotifystats",
                        host=postgres_host(),
                        user=postgres_user(),
                        password=postgres_password(),
                        port=postgres_port())

cursor = conn.cursor()

with open("./data/sql/schema.sql") as f:
    schema = f.read()
    cursor.execute(schema)

conn.commit()
