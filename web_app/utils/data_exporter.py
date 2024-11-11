import csv
import io
import json
import tempfile


class DataExporter:
    @staticmethod
    def export_to_json(data: list[dict], filename: str) -> str:
        """
        Export data to a JSON file and return the file path.
        """
        with tempfile.NamedTemporaryFile(delete=False, mode="w", newline="", suffix=".json") as temp_file:
            json.dump(data, temp_file)
            temp_file_path = temp_file.name
        return temp_file_path

    @staticmethod
    def export_to_csv(data: list[dict], filename: str) -> io.StringIO:
        """
        Export data to a CSV file (in memory) and return the CSV content.
        """
        csv_data = io.StringIO()
        if data:
            writer = csv.DictWriter(csv_data, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            csv_data.seek(0)
        return csv_data
