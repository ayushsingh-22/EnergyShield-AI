FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false

COPY pyproject.toml ./
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
