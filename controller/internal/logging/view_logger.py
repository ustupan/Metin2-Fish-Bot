import datetime


def add_newlines(value):
    return value + "\n\n"


def add_time(value):
    current_time = datetime.datetime.now()
    time_only = current_time.strftime("%H:%M:%S")
    return "[" + time_only + "] " + value


class ViewLogger:

    def __init__(self, update_view_logs: callable):
        self.update_view_logs = update_view_logs

    def update_logs(self, value):
        self.update_view_logs(add_newlines(add_time(value)))
