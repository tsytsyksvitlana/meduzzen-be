from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)


class UserNotFoundException(ObjectNotFoundException):
    def __init__(self, user_id: int):
        super().__init__(object_type="User", object_id=user_id)


class UserAlreadyExistsException(ObjectAlreadyExistsException):
    def __init__(self, user_id: int):
        super().__init__(object_type="User", object_id=user_id)
