class DataNotFoundException(Exception):
    def __init__(self, detail: str = "No data available for export."):
        self.detail = detail
