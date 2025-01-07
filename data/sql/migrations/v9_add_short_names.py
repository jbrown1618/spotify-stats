from data.sql.migrations.migration import Migration
from utils.name import short_name

remove_short_names = """
ALTER TABLE track
DROP COLUMN short_name;

ALTER TABLE album
DROP COLUMN short_name;
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


    def migrate(self, cursor):
        cursor.execute(add_short_names)

        cursor.execute("SELECT uri, name FROM track")
        track_rows = cursor.fetchall()
        for uri, name in track_rows:
            cursor.execute(
                "UPDATE track SET short_name = %(short_name)s WHERE uri = %(uri)s", 
                {"short_name": short_name(name), "uri": uri}
            )

        cursor.execute("SELECT uri, name FROM album")
        album_rows = cursor.fetchall()
        for uri, name in album_rows:
            cursor.execute(
                "UPDATE album SET short_name = %(short_name)s WHERE uri = %(uri)s", 
                {"short_name": short_name(name), "uri": uri}
            )


    def reverse(self, cursor):
        cursor.execute(remove_short_names)


if __name__ == '__main__':
    AddShortNames().reverse_migration()
    AddShortNames().perform_migration()
