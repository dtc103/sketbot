class InvalidRoleException(Exception):
    pass


class DatabaseException(Exception):
    def __init__(self, reason=""):
        self.reason = reason

    pass
