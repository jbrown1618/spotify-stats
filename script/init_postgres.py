from data.raw import get_connection

conn = get_connection()
cursor = conn.cursor()

with open("./data/sql/schema.sql") as f:
    schema = f.read()
    cursor.execute(schema)

conn.commit()
