# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5000

# Run under gunicorn — never the Flask dev server. The data generator runs
# as a separate worker service, so multiple web workers are safe; tune with
# the WEB_CONCURRENCY env var (gunicorn reads it).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]