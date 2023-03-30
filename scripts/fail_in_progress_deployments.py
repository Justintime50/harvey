from sqlitedict import SqliteDict  # type: ignore

from harvey.config import Config


# This script will change "in-progress" deployments to "failed" if they get stuck

DATABASE_LOCATION = Config.database_file
DEPLOYMENTS_TABLE_NAME = 'deployments'


def main():
    with SqliteDict(filename=DATABASE_LOCATION, tablename=DEPLOYMENTS_TABLE_NAME) as deployments_table:
        for key, data in deployments_table.items():
            for index, attempt in enumerate(data.get('attempts')):
                if deployments_table[key]['attempts'][index]['status'] == 'In-Progress':
                    # sqlitedict doesn't know about dictionaries in memory, must be assigned back
                    data['attempts'][index]['status'] = 'Failure'
                    deployments_table[key] = data
                    print(f'{key} status updated from "In-Progress" to "Failure"!')

        deployments_table.commit()

    print('All "In-Progress" deployments have been changed to "Failure".')


if __name__ == '__main__':
    main()
