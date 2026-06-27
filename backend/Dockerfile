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

# Run under gunicorn — never the Flask dev server. A single worker keeps
# one data-generator thread until the generator moves to its own worker
# process (issue #15).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:create_app()"]