# Slim python image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into container
COPY yournews/ /app/

# Expose the app's port
EXPOSE 8000

# Command to run the dev server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]