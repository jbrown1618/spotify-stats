from data.sql.migrations.migration import Migration

drop_table = """
DROP TABLE IF EXISTS audio_features;
"""


class RemoveAudioFeatures(Migration):
    def __init__(self):
        super().__init__("v13")


    def migrate(self, cursor):
        cursor.execute(drop_table)

    def reverse(self, _):
        print('Cannot reverse this migration')


if __name__ == '__main__':
    RemoveAudioFeatures().perform_migration()
