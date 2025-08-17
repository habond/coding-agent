# Use Python slim image for smaller attack surface
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY config.json .
COPY mypy.ini .
COPY pytest.ini .
COPY pyproject.toml .

# Copy tests for development
COPY tests/ tests/

# Create .env file placeholder (user will mount real one)
RUN touch .env

# Create sandbox directory for assistant working area
RUN mkdir -p /app/sandbox

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (if needed for future web interface)
EXPOSE 8000

# Default command
CMD ["python", "src/main.py"]
