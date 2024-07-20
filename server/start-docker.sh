#!/bin/bash

# Stop and remove the existing container if it's running
if [ "$(docker ps -q -f name=transcription-app)" ]; then
    echo "Stopping and removing existing container..."
    docker stop transcription-app
    docker rm transcription-app
fi

# Build the Docker image
echo "Building the Docker image..."
docker build -t transcription-app .

# Run the Docker container
echo "Running the Docker container..."
docker run -d -p 80:80 --name transcription-app transcription-app