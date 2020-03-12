import os


def normalize_db_uri():
    if os.name == "nt":
        return os.getcwd()[3:].replace("\\", "/") + "/"
    return os.getcwd()[1:] + "/"


URI_BASE_DIR = normalize_db_uri()


class Configuration:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'sqlite:////{URI_BASE_DIR}db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    METRO_STATION_URL = "https://api.hh.ru/metro/1"
