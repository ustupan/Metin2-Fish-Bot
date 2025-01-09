class DemoException(Exception):
    def __init__(self, exceptions):
        self.exceptions = exceptions
        self.message = "Demo exceptions - exit the bot!"
