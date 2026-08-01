# ── Stage 1: Build wheels (including all transitive dependencies) ─────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps needed to compile C extensions (psycopg2, numpy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt
#                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   No --no-deps here: pip resolves the full dependency tree and
#   builds wheels for every package (direct + transitive), so stage 2
#   can install everything offline without hitting PyPI.

# ── Stage 2: Production image ────────────────────────────────────────────────
FROM python:3.11-slim AS production

# Security: non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Runtime-only system libs (no build tools — keeps image small)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder stage
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

# Install from local wheels only — no network needed
RUN pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt
#               ^^^^^^^^^^^^^^
#   --no-cache-dir (not --no-cache) is the correct flag.
#   --find-links tells pip where to look; all deps are present because
#   we built them without --no-deps in stage 1.

# Copy application source
COPY ./intelligence_engine /app/intelligence_engine
COPY ./data_pipeline       /app/data_pipeline
COPY ./backend             /app/backend

# Grant ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
