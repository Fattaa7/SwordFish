FROM python:3.11-slim
# Use the official slim Python 3.11 image as the base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Set the working directory inside the container to /app

# Copy requirements first for better caching
COPY Fish/requirements.txt .
# Copy requirements.txt from your project into the container

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Install Python dependencies listed in requirements.txt

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
# Switch to non-root user
USER app

# Expose port
EXPOSE 8000
# Inform Docker that the container will listen on port 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# Set the default command to run the FastAPI app using Uvicorn on port 8000, accessible from any network interface
