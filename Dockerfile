# =============================================================================
# Enterprise Agentic Platform - Dockerfile
# Multi-stage build for production deployment
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Frontend Build
# -----------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --silent || npm install

# Copy frontend source
COPY frontend/ ./

# Build for production (creates dist folder)
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Python Runtime + Final Image
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PORT=8000 \
    HOST=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy skills directory
COPY .skills/ ./.skills/

# Copy configuration
COPY config.yaml ./

# Copy run script
COPY run.py ./

# Copy docker entrypoint
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Create frontend directory structure
RUN mkdir -p ./frontend/dist ./frontend/public/mascot

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# Copy frontend public assets (logo, mascot)
COPY frontend/public/ ./frontend/public/

# Create necessary directories
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Entry point
ENTRYPOINT ["./docker-entrypoint.sh"]
