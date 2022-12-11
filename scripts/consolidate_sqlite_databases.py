import os
import shutil

from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config


# This script consolidates the multiple `locks` and `pipeline` database files into a single
# sqlite database file and places them in their respective tables.

# NOTE: This script will remove the `databases` directory

LOCKS_DATABASE_LOCATION = os.path.join(Config.harvey_path, 'stores', 'locks.sqlite')
PIPELINE_DATABASE_LOCATION = os.path.join(Config.harvey_path, 'stores', 'deployments.sqlite')  # AKA: pipelines.sqlite
NEW_SINGLE_DATABASE_LOCATION = Config.database_file
DATABASES_LOCATION = os.path.join(Config.harvey_path, 'databases')

LOCKS_TABLE_NAME = 'locks'
DEPLOYMENTS_TABLE_NAME = 'deployments'


def main():
    # Start a new `databases` directory
    if os.path.exists(DATABASES_LOCATION):
        shutil.rmtree(DATABASES_LOCATION, ignore_errors=True)
    os.mkdir(DATABASES_LOCATION)

    # Locks
    with SqliteDict(filename=NEW_SINGLE_DATABASE_LOCATION, tablename=LOCKS_TABLE_NAME) as locks_table:
        with SqliteDict(filename=LOCKS_DATABASE_LOCATION) as old_locks_file:
            for key, value in old_locks_file.items():
                locks_table[key] = value

        locks_table.commit()

    print('Locks consolidated.')

    # Deployments
    with SqliteDict(filename=NEW_SINGLE_DATABASE_LOCATION, tablename=DEPLOYMENTS_TABLE_NAME) as deployments_table:
        with SqliteDict(filename=PIPELINE_DATABASE_LOCATION) as old_pipeline_file:
            for key, value in old_pipeline_file.items():
                deployments_table[key] = value

        deployments_table.commit()

    print('Deployments consolidated.')

    # Validation
    print('\nThe following are the contents of the new datbase file:\n')
    with SqliteDict(filename=NEW_SINGLE_DATABASE_LOCATION, tablename=LOCKS_TABLE_NAME) as table:
        for key, value in table.items():
            print(key, value)
    with SqliteDict(filename=NEW_SINGLE_DATABASE_LOCATION, tablename=DEPLOYMENTS_TABLE_NAME) as table:
        for key, value in table.items():
            print(key, value)
    print('\nPlease manually remove the "stores" directory once you are happy with the migration results.')


if __name__ == '__main__':
    main()
