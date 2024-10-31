class PermissionDeniedException(Exception):
    def __init__(
            self,
            detail: str = "You don't have permission to perform this action."
    ):
        self.detail = detail
        super().__init__(self.detail)
