# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
# RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

# Copy the rest of the application code into the container
COPY . .

# Copy the .env file into the container
COPY .env .
# Expose the port that the app runs on
EXPOSE 9999

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9999"]