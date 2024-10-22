# Meduzzen Backend Internship
[![Python](https://img.shields.io/badge/-Python-%233776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0a0a0a)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-1B5B25?style=for-the-badge&logo=pydantic&logoColor=white&labelColor=0a0a0a)](https://pydantic-docs.helpmanual.io/)
[![Pytest](https://img.shields.io/badge/Pytest-0A9B38?style=for-the-badge&logo=pytest&logoColor=white&labelColor=0a0a0a)](https://pytest.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white&labelColor=0a0a0a)](https://www.docker.com/)

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
poetry install --without dev --no-root
```
2. Run the application:
```
poetry run uvicorn web_app.main:app
```
Visit http://{SERVER_HOST}:{SERVER_PORT}}/ in your web browser to access the application.
3. Run in Docker:
```
docker build -f Dockerfile.prod -t meduzzen_be .
docker run -p 8000:8000 --env-file .env meduzzen_be
```
To stop use
```
docker stop fastapi_container
```
5. Create a docker network
```
docker network create home
```
6. Run in docker compose in detached mode
```
docker compose up -d --build
```
7. To stop the running services:
```
docker compose down
```
# Development
***
To run the application in development mode:
1. Install development dependencies:
```
poetry install --with dev
```
2. Run the application with auto-reload:
```
poetry run uvicorn web_app.main:app --reload
```
Visit http://localhost:8000/ in your web browser to access the application.
3. Run app in Docker:
```
docker build -f Dockerfile.prod -t meduzzen_be .
docker run -p 8000:8000 --env-file .env meduzzen_be
```
4. Run tests in Docker:
```
docker build -f Dockerfile.test -t meduzzen_be_test .
docker run --env-file .env meduzzen_be_test
```
To stop use
```
docker stop fastapi_container
```
5. Create a docker network
```
docker network create home
```
6. Run in docker compose in detached mode
```
docker compose up -d --build
```
7. To stop the running services:
```
docker compose down
```
### Migrations
```
docker exec -it -w /code/web_app meduzzen-be-fastapi-1 /bin/sh
```
```
PYTHONPATH=/code alembic revision --autogenerate -m "message"
```
```
export PYTHONPATH=/code
alembic upgrade head
```
```
exit
```
### To run tests
```
poetry run pytest
```
### Pre-commit command
```
poetry run pre-commit run --all-files
```
