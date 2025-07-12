# Use the official Python image from the Docker Hub
FROM python:3.11-slim

RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt --timeout 1000
# RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Copy the rest of the application code into the container
COPY . .

# Copy the .env file into the container
COPY .env .
# Expose the port that the app runs on
EXPOSE 9999

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9999"]