import datetime


def add_newlines(value):
    return value + "\n\n"


def add_time(value):
    current_time = datetime.datetime.now()
    time_only = current_time.strftime("%H:%M:%S")
    return "[" + time_only + "] " + value

def write_to_file(log_message, app_identifier):

    app_identifier = app_identifier.split("| ", 1)[1]
    file = app_identifier + "logs.txt"
    safe_log_message = ''.join(char if char.isprintable() else '?' for char in log_message)
    with open(file, "a") as log_file:
        log_file.write(safe_log_message)

def determine_process_and_(log_message):
    with open("logs.txt", "a") as log_file:
        log_file.write(log_message)

class ViewLogger:

    app_id = "none"

    def __init__(self, update_view_logs: callable):
        self.update_view_logs = update_view_logs

    def update_logs(self, value):
        log_message = add_newlines(add_time(value))
        self.update_view_logs(log_message)
        write_to_file(log_message, self.app_id)

