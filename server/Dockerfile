# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.10-slim 

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# RUN python -m "from whisper import load_model; load_model('small')"
RUN python -c "from whisper import load_model; load_model('small')"

RUN apt-get update && apt-get install -y ffmpeg
# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run main.py when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "2"]