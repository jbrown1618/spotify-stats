import os
from retrieve.save_data import save_data
from summarize.summarize import summarize_results
from dotenv import load_dotenv


def main():
    load_dotenv()

    output_dir = os.getenv("OUTPUT_DIR")
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    save_data(output_dir, spotify_client_id, spotify_client_secret)
    summarize_results(output_dir)


if __name__ == '__main__':
    main()