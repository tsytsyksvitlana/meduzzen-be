class AuthorizationException(Exception):
    def __init__(self, detail: str = "Authorization error"):
        self.detail = detail
        super().__init__(self.detail)


class TokenExpiredException(AuthorizationException):
    def __init__(self):
        super().__init__(detail="Token has expired")
