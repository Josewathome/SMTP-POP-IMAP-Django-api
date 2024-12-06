# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY ./src /app/

COPY .env /app/.env

# Collect static files (even though you don't have them, it's good practice)
RUN python manage.py collectstatic --noinput

# Expose the application port
EXPOSE 8000

# Set the default command to gunicorn (Django WSGI application)
CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8010"]
