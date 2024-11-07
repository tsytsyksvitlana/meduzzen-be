from web_app.exceptions.application import BadRequestException


class MembershipException(BadRequestException):
    def __init__(self, detail: str):
        super().__init__(detail)
