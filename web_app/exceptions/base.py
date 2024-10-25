from fastapi import HTTPException, status


class ObjectNotFoundException(HTTPException):
    def __init__(self, object_type: str, object_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{object_type} with ID {object_id} not found."
        )


class ObjectAlreadyExistsException(HTTPException):
    def __init__(self, object_type: str, object_id: int):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{object_type} with ID {object_id} already exists."
        )
