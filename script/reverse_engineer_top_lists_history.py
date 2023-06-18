import pandas as pd
import sys
import os
import subprocess
from datetime import datetime

"""
Previous versions only saved top track and artists data at the given time.

We can do a lot more if we persist that data over time, but only starting
collection now loses out on a bunch of data that we actually have, because the
output was in a git repo.

This script goes back in time through the git repo and merges together old
versions of top_tracks and top_albums.

Usage:
  python script/reverse_engineer_top_lists_history.py path/to/output/directory
"""


def reverse_engineer_top_lists_history():
    output_dir = sys.argv[1]
    if not os.path.isdir(output_dir):
        print(f'Output path {output_dir} does not exist')
        return

    if not os.path.isdir(os.path.join(output_dir, '.git')):
        print(f'Output path {output_dir} is not a git repository')
        return
    
    old_top_tracks_path = os.path.join(output_dir, 'data', 'top_tracks.csv')
    old_top_artists_path = os.path.join(output_dir, 'data', 'top_artists.csv')
    if not os.path.isfile(old_top_tracks_path):
        print('No top tracks data in the old format; no work to do')
        return
    
    top_tracks = None
    top_artists = None
    done = False
    
    while not done:
        date = get_current_commit_date(output_dir)
        print(f'Getting data for {date}')
        top_tracks_for_date = pd.read_csv(old_top_tracks_path)
        top_tracks_for_date['as_of_date'] = date
        top_artists_for_date =  pd.read_csv(old_top_artists_path)
        top_artists_for_date['as_of_date'] = date

        if top_tracks is None:
            top_tracks = top_tracks_for_date
            top_artists = top_artists_for_date
        else:
            top_tracks = pd.concat([top_tracks, top_tracks_for_date], axis=0)
            top_artists = pd.concat([top_artists, top_artists_for_date], axis=0)

        go_back_in_time(date, output_dir)
        done = not os.path.isfile(old_top_tracks_path)

    return_to_present(output_dir)

    os.remove(old_top_tracks_path)
    os.remove(old_top_artists_path)

    top_tracks_dir = os.path.join(output_dir, 'data', 'top_tracks')
    top_artists_dir = os.path.join(output_dir, 'data', 'top_artists')
    os.mkdir(top_tracks_dir)
    os.mkdir(top_artists_dir)

    years = top_tracks['as_of_date'].apply(lambda d: d[0:4]).unique()
    for year in years:
        print('Saving data for {year}')
        top_tracks_for_year = top_tracks[top_tracks['as_of_date'].apply(lambda d: d[0:4]) == year]
        top_artists_for_year = top_artists[top_artists['as_of_date'].apply(lambda d: d[0:4]) == year]

        top_tracks_for_year.to_csv(os.path.join(top_tracks_dir, f'{year}.csv'), index=False)
        top_artists_for_year.to_csv(os.path.join(top_artists_dir, f'{year}.csv'), index=False)

        
def go_back_in_time(date: str, output_dir: str) -> bool:
    d1 = datetime.strptime(date, '%Y-%m-%d')
    d2 = None
    diff = None

    while diff == None or diff < 3:
        go_to_previous_commit(output_dir)
        d2 = datetime.strptime(get_current_commit_date(output_dir), '%Y-%m-%d')
        diff = (d1 - d2).days
        

def go_to_previous_commit(output_dir):
    process = subprocess.Popen(['git', 'reset', '--hard', 'HEAD~1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=output_dir)
    out, err = process.communicate()
    # if err.decode('utf-8') != '':
    #     raise Exception(err)

def get_current_commit_date(output_dir):
    process = subprocess.Popen(['git', 'show', '-s', r'--format=%ci', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=output_dir)
    out, err = process.communicate()
    if err.decode('utf-8') != '':
        raise Exception(err)
    
    return out.decode('utf-8')[0:10]


def return_to_present(output_dir):
    process = subprocess.Popen(['git', 'reset', '--hard', 'origin/main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=output_dir)
    out, err = process.communicate()
    # if err.decode('utf-8') != '':
    #     raise Exception(err)


if __name__ == '__main__':
    reverse_engineer_top_lists_history()
