# Use a Python base image optimized for production
FROM python:3.12-slim

# Set environment variables for Cloud Run
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Copy requirements file for better layer caching
COPY requirements.txt ./

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ app/

# Expose the port that Cloud Run expects
EXPOSE 8080

# Use direct uvicorn command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]