# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3.11-slim
WORKDIR /app

# Copy installed dependencies
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy only the necessary backend application code
COPY app/ app/
COPY data/ data/
COPY frontend/ frontend/
COPY index.html .

# Expose port
EXPOSE 8000

# Run the API
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
