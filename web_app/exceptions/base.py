class ObjectNotFoundException(Exception):
    def __init__(self, object_type: str, field: str):
        self.object_type = object_type
        self.field = field

    def __str__(self):
        return f"{self.object_type} with {self.field} not found."


class ObjectAlreadyExistsException(Exception):
    def __init__(self, object_type: str, field: str):
        self.object_type = object_type
        self.field = field

    def __str__(self):
        return f"{self.object_type} with {self.field} already exists found."
