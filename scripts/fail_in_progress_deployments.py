from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config


# This script will change "in-progress" deployments to "failed" if they get stuck

DATABASE_LOCATION = Config.database_file
DEPLOYMENTS_TABLE_NAME = 'deployments'


def main():
    # Deployments
    with SqliteDict(filename=DATABASE_LOCATION, tablename=DEPLOYMENTS_TABLE_NAME) as deployments_table:
        for key, data in deployments_table.iteritems():
            if data['status'] == 'In-Progress':
                deployments_table[key]['status'] = 'Failure'
                print(f'{key} status updated from "In-Progress" to "Failure"!')

        deployments_table.commit()

    print('All "In-Progress" deployments have been changed to "Failure".')


if __name__ == '__main__':
    main()
