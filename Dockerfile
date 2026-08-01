# Stage 1: Build Layer
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system build dependencies required for compiling certain Python extensions (like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a localized wheel directory
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# Stage 2: Production Layer
FROM python:3.11-slim AS production

# Security: Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install runtime database libraries required by psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-compiled Python packages from builder stage
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

RUN pip install --no-cache --no-index /wheels/*

# Copy the actual application source code
COPY ./intelligence_engine /app/intelligence_engine
COPY ./data_pipeline /app/data_pipeline
COPY ./backend /app/backend

# Grant ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Default launch command: runs FastAPI via Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
