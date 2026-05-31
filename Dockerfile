FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir ".[dev]"

COPY . .
EXPOSE 8050

CMD ["python", "-m", "app.main"]

