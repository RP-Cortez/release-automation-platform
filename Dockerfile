# ==========================================
# Stage 1: Build & Dependency Stage
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# Stage 2: Minimal Runtime Stage
# ==========================================
FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Create a non-root system user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source and configuration schema
COPY src/ /app/src/
COPY schema/ /app/schema/

# Set file permissions for non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user context
USER appuser

# Entrypoint executes the validation tool inside the container
ENTRYPOINT ["python", "src/validator.py"]
