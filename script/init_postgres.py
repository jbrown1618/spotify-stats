from data.raw import get_connection

with open("./data/sql/schema.sql") as f, get_connection() as conn:
    schema = f.read()
    cursor = conn.cursor()
    cursor.execute(schema)
    conn.commit()
