from web_app.exceptions.base import ObjectNotFoundException


class NoDataToExportException(ObjectNotFoundException):
    def __init__(self, message="No data available for export."):
        super().__init__(message, field=None)

    def __str__(self):
        return "No data available for export."
