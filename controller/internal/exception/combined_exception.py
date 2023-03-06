class CombinedException(Exception):
    def __init__(self, exceptions):
        self.exceptions = exceptions
        self.message = "Multiple exceptions occurred: "
        for exc in exceptions:
            self.message += f"{str(exc)}, "
        super().__init__(self.message[:-2])
