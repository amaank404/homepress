class HomepressException(Exception):
    pass

class UnknownInputFormat(HomepressException):
    pass

class CLIUnknownBindType(HomepressException):
    pass