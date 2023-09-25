from tasks.save_supplemental_data import save_supplemental_data
from tasks.save_spotify_data import save_spotify_data
from tasks.generate_output import generate_output
from utils.settings import should_generate_output, should_save_spotify_data, should_save_supplemental_data


def main():
    if should_save_spotify_data():
        save_spotify_data()

    if should_save_supplemental_data():
        save_supplemental_data()

    if should_generate_output():
        generate_output()


if __name__ == '__main__':
    main()