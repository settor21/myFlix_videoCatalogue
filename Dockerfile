# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenSSL (required for MongoDB SSL)
RUN apt-get update && apt-get install -y openssl

# Copy the MongoDB certificate and key into the container
COPY /home/amedikusettor/mongoAuth/mongodb-cert.pem /app
COPY /home/amedikusettor/mongoAuth/mongodb-key.pem /app

# Set environment variable for GCP JSON key
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/devopsfinalproject-4d723fcf8c7e.json

# Set environment variable for MongoDB certificate and key paths
ENV MONGODB_CERT_PATH=/app/mongodb-cert.pem
ENV MONGODB_KEY_PATH=/app/mongodb-key.pem

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]