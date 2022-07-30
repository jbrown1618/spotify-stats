from retrieve.save_data import save_data
from summarize.summarize import summarize_results
from utils.settings import init_settings, skip_data_fetching


def main():
    init_settings()
    if not skip_data_fetching():
        save_data()
    summarize_results()


if __name__ == '__main__':
    main()