FROM python:3.11.0
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
RUN pip install poetry

WORKDIR /backend
COPY ./poetry.lock ./pyproject.toml ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY . .

#ENTRYPOINT [ "sh", "entrypoint.sh" ]
ENTRYPOINT alembic upgrade head; python src/main.py
