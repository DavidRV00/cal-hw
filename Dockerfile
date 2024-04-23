FROM python:latest

WORKDIR /code

COPY ./pyproject.toml ./
COPY ./src ./src
COPY ./data ./data

RUN pip install -e .

RUN pip list

CMD ["hypercorn", "calendar_app.api.main:app", "--reload", "--bind", "0.0.0.0:8000"]




