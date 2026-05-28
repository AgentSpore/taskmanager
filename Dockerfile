FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir uv && uv pip install --no-cache-dir --frozen --no-dev .

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /app /app
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "taskmanager.main:app", "--host", "0.0.0.0", "--port", "8000"]