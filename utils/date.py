from datetime import datetime


def this_date():
    return datetime.today().strftime('%Y-%m-%d')