FROM python:3.12

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.8.0

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /code

COPY pyproject.toml poetry.lock /code/

RUN poetry install --no-interaction --no-ansi

COPY . /code/

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "web_app.main:app", "--reload"]
