from web_app.exceptions.base import (
    ObjectAlreadyExistsException,
    ObjectNotFoundException
)


class JoinRequestAlreadyExistsException(ObjectAlreadyExistsException):
    def __init__(self, join_request_id: int):
        super().__init__(object_type="JoinRequest", field=f"ID {join_request_id}")


class JoinRequestNotFoundException(ObjectNotFoundException):
    def __init__(self, request_id: int):
        super().__init__(
            object_type="JoinRequest", field=f"ID {request_id}"
        )
