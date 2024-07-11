# Use the official Python image from the Python 3.12 slim variant
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install dependencies
RUN apt-get update && \
    apt-get install -y build-essential ffmpeg libsm6 libxext6 && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean

# Copy the rest of the application code into the container
COPY . /app/

# Expose port 5000 to the outside world
EXPOSE 5000

# Define the command to run the application
CMD ["python", "run.py"]
