import sqlalchemy
from data.raw import get_engine

get_latest_version = """
SELECT v.version FROM version v
WHERE v.timestamp = (
    SELECT max(timestamp) from version
)
"""

update_version = """
INSERT INTO version (version) VALUES (:version)
"""

class Migration:
    __version = None

    def __init__(self, version):
        self.__version = version


    def perform_migration(self):
        with get_engine().connect() as conn:
            try:
                result = conn.execute(sqlalchemy.text(get_latest_version))
                current_version = result.fetchone()[0]

                if int(current_version[1:]) >= int(self.__version[1:]):
                    print(f'Current version is {current_version}; skipping migration to {self.__version}')
                    return True
                
                print(f'Beginning migration to {self.__version}')
                self.migrate(conn)

                conn.execute(sqlalchemy.text(update_version), {"version": self.__version})
                conn.commit()
                print(f'Completed migration to {self.__version}')
                return True
            except Exception as e:
                print(f'Migration to {self.__version} failed: {e}')
                conn.rollback()
                return False


    def reverse_migration(self):
        with get_engine().connect() as conn:
            try:
                result = conn.execute(sqlalchemy.text(get_latest_version))
                current_version = result.fetchone()[0]

                if int(current_version[1:]) != int(self.__version[1:]):
                    print(f'Current version is {current_version}; skipping reversal of {self.__version}')
                    return True
                
                print(f'Reversing migration to {self.__version}')
                self.reverse(conn)

                conn.execute(sqlalchemy.text(update_version), {"version": f"v{int(self.__version[1:]) - 1}"})
                conn.commit()
                print(f'Reversed migration to {self.__version}')
                return True
            except Exception as e:
                print(f'Reversing migration to {self.__version} failed: {e}')
                conn.rollback()
                return False


    def migrate(self, conn):
        raise NotImplementedError('Subclasses must implement migrate()')


    def reverse(self, conn):
        raise NotImplementedError('Subclasses must implement reverse()')
