import sqlalchemy
from data.raw import get_engine

with open("./data/sql/schema.sql") as f:
    schema = f.read()
    with get_engine().begin() as conn:
        conn.execute(sqlalchemy.text(schema))
