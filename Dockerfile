# Use the official Python image from the Docker Hub
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Install Gunicorn using pip
RUN pip install gunicorn

# Copy the rest of the application code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create directory for static files
RUN mkdir -p /industrialpartner/static/
# Expose port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "industrialpartner_app.wsgi:application"]