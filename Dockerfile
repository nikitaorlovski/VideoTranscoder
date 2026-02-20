FROM python:3.12-bookworm

ENV PIP_NO_CACHE_DIR=1 POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install --upgrade poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY . /app

WORKDIR /app

CMD alembic -c /app/alembic.ini upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
