class InvalidFieldException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class InvalidPasswordException(InvalidFieldException):
    def __init__(self):
        self.detail = (
            "Password must be 8-24 characters long, contain digits, "
            "lowercase and uppercase letters of any alphabet, "
            "and special characters except for @, \", ', <, >."
        )
        super().__init__(self.detail)
