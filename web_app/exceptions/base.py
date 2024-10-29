class ObjectNotFoundException(Exception):
    def __init__(self, object_type: str, object_id: int):
        self.object_type = object_type
        self.object_id = object_id


class ObjectAlreadyExistsException(Exception):
    def __init__(self, object_type: str, object_id: int):
        self.object_type = object_type
        self.object_id = object_id
