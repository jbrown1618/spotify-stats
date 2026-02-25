import sqlalchemy
from data.raw import get_engine

with open("./data/sql/schema.sql") as f, get_engine().begin() as conn:
    schema = f.read()
    conn.execute(sqlalchemy.text(schema))
