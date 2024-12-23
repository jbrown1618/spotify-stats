from jobs.save_supplemental_data import save_supplemental_data
from jobs.save_spotify_data import save_spotify_data
from tasks.generate_output import generate_output
from utils.fonts import install_fonts
from utils.settings import should_generate_output, should_save_spotify_data, should_save_supplemental_data


def main():
    if should_save_spotify_data():
        save_spotify_data()
    else:
        print('Skipping saving spotify data')

    if should_save_supplemental_data():
        save_supplemental_data()
    else:
        print('Skipping saving supplemental data')

    if should_generate_output():
        install_fonts()
        generate_output()
    else:
        print('Skipping generating output')


if __name__ == '__main__':
    main()
