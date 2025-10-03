import datetime


def get_open_close_time(date, hour):
    date_time = datetime.datetime.combine(date, datetime.datetime.min.time())
    return date_time.replace(hour=hour, minute=0, second=0, microsecond=0)
