import os
from dotenv import load_dotenv

settings = {
    "output_dir": "./output",
    "spotify_client_id": "",
    "spotify_client_secret": ""
}


def init_settings():
    load_dotenv()
    set_output_dir(os.getenv("OUTPUT_DIR"))
    set_spotify_client_id(os.getenv("SPOTIFY_CLIENT_ID"))
    set_spotify_client_secret(os.getenv("SPOTIFY_CLIENT_SECRET"))


def set_output_dir(output_dir):
    settings["output_dir"] = output_dir


def output_dir():
    return settings["output_dir"]


def set_spotify_client_id(id):
    settings["spotify_client_id"] = id


def spotify_client_id():
    return settings["spotify_client_id"]


def set_spotify_client_secret(secret):
    settings["spotify_client_secret"] = secret
    

def spotify_client_secret():
    return settings["spotify_client_secret"]
