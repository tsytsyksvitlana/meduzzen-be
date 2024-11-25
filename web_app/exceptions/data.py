class DataNotFoundException(Exception):
    def __init__(self, detail: str = "No data available for export_data."):
        self.detail = detail
