from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)


class UserIdNotFoundException(ObjectNotFoundException):
    def __init__(self, user_id: int):
        super().__init__(object_type="User", field=f"ID {user_id}")


class UserEmailNotFoundException(ObjectNotFoundException):
    def __init__(self, email: str):
        super().__init__(object_type="User", field=f"email {email}")


class UserIdAlreadyExistsException(ObjectAlreadyExistsException):
    def __init__(self, user_id: int):
        super().__init__(object_type="User", field=f"ID {user_id}")
