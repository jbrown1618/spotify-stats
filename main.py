from retrieve.save_data import save_data
from summarize.summarize import summarize_results
from utils.settings import init_settings, output_dir, spotify_client_id, spotify_client_secret


def main():
    init_settings()
    save_data()
    summarize_results()


if __name__ == '__main__':
    main()