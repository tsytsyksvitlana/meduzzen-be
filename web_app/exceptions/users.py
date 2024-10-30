from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)


class UserIdNotFoundException(ObjectNotFoundException):
    def __init__(self, user_id: int):
        super().__init__(object_type="User", object_id=user_id)


class UserEmailNotFoundException(ObjectNotFoundException):
    def __init__(self, email: str):
        super().__init__(object_type="User", object_id=email)


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    def __init__(self, user_id: int):
        super().__init__(object_type="User", object_id=user_id)
