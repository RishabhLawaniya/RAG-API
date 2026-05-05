# Use Python 3.11 — stable, widely supported
# (we avoid 3.14 in production as it's too new)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker caches this layer)
# Only re-installs packages if requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of application code
COPY . .

# Create uploads folder
RUN mkdir -p uploads

# Expose port 8000
EXPOSE 8000

# Default command — start FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]