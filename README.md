# Meduzzen Backend Internship
[![Python](https://img.shields.io/badge/-Python-%233776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0a0a0a)](https://fastapi.tiangolo.com/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9B38?style=for-the-badge&logo=pytest&logoColor=white&labelColor=0a0a0a)](https://pytest.org/)

# Generic Setup
***
1. Create and activate the virtual environment:
```
poetry install
```
This will create a virtual environment and install all dependencies specified in pyproject.toml.
2. Fill the .env file (use .env.sample as an example).
***
# Production
***
To run the application in production:
1. Install dependencies (if not done already):
```
poetry install
```
2. Run the application:
```
poetry run uvicorn web_app.main:app
```
Visit http://{SERVER_HOST}:{SERVER_PORT}}/ in your web browser to access the application.
# Development
***
To run the application in development mode:
1. Install development dependencies:
```
poetry install --dev
```
2. Run the application with auto-reload:
```
poetry run uvicorn web_app.main:app --reload
```
Visit http://localhost:8000/ in your web browser to access the application.
### To run tests
```
poetry run pytest
```
### Pre-commit command
```
poetry run pre-commit run --all-files
```
