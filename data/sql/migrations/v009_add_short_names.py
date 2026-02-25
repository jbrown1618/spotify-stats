from data.sql.migrations.migration import Migration
from utils.name import short_name
import sqlalchemy

remove_short_names = """
ALTER TABLE track
DROP COLUMN IF EXISTS short_name;

ALTER TABLE album
DROP COLUMN IF EXISTS short_name;
"""

add_short_names = """
ALTER TABLE track
ADD short_name TEXT DEFAULT '';

ALTER TABLE album
ADD short_name TEXT DEFAULT '';
"""

class AddShortNames(Migration):
    def __init__(self):
        super().__init__("v9")


    def migrate(self, conn):
        conn.execute(sqlalchemy.text(remove_short_names))
        conn.execute(sqlalchemy.text(add_short_names))

        result = conn.execute(sqlalchemy.text("SELECT uri, name FROM track"))
        track_rows = result.fetchall()
        for uri, name in track_rows:
            short = short_name(name)
            if short != name:
                print(f'Updating {name} --> {short}')
                
            conn.execute(
                sqlalchemy.text("UPDATE track SET short_name = :short_name WHERE uri = :uri"), 
                {"short_name": short, "uri": uri}
            )

        result = conn.execute(sqlalchemy.text("SELECT uri, name FROM album"))
        album_rows = result.fetchall()
        for uri, name in album_rows:
            short = short_name(name)
            if short != name:
                print(f'Updating {name} --> {short}')

            conn.execute(
                sqlalchemy.text("UPDATE album SET short_name = :short_name WHERE uri = :uri"), 
                {"short_name": short, "uri": uri}
            )


    def reverse(self, conn):
        conn.execute(sqlalchemy.text(remove_short_names))


if __name__ == '__main__':
    AddShortNames().reverse_migration()
    AddShortNames().perform_migration()
