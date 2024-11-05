class ApplicationErrorException(Exception):
    def __init__(self, detail: str = "An error has occurred."):
        self.detail = detail
        super().__init__(self.detail)
