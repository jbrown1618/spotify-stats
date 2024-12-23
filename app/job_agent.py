from time import sleep

from jobs.execute import execute_next_job


def main():
    print('Running job agent...')
    while True:
        executed = execute_next_job()
        if not executed:
            sleep(120)


if __name__ == "__main__":
    main()