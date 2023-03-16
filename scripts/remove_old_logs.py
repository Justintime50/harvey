import os
import time


# This script removes old log files for uWSGI, useful to run on a cron


LOG_FOLDER = os.path.join(os.path.expanduser('~/harvey'), 'logs')
LOG_LIFE_IN_DAYS = 14
DAY_IN_SECONDS = 86400
LOG_LIFE = DAY_IN_SECONDS * LOG_LIFE_IN_DAYS


def main():
    list_of_files = os.listdir(LOG_FOLDER)
    current_time = time.time()

    for filename in list_of_files:
        file_location = os.path.join(LOG_FOLDER, filename)
        file_created_at = os.stat(file_location).st_ctime
        file_age = file_created_at + LOG_LIFE
        if current_time > file_age:
            print(f"Deleting: {file_location}...")
            os.remove(file_location)


if __name__ == '__main__':
    main()
