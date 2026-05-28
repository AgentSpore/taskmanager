FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN python -m pip install --upgrade pip && pip install hatchling
RUN hatch build -t wheel

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl
EXPOSE 8000
CMD ["uvicorn", "taskmanager.main:app", "--host", "0.0.0.0", "--port", "8000"]