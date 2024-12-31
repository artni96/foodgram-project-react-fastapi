FROM python:3.11.0
RUN apt-get update
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install poetry

WORKDIR /backend
COPY ./poetry.lock ./pyproject.toml ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi
RUN apt-get install wkhtmltopdf -y

COPY . .

ENTRYPOINT alembic upgrade head; python src/main.py
