## Generate Live Transcript of any stream on Thetacloud


## What it does?
This project enables real-time transcription of live video streams on Thetacloud. It consists of two main components:

1. A server that handles stream ingestion, transcription, and data storage.
2. A client application that displays the live video stream alongside its real-time transcription.

Key features include:

- Live transcription of ongoing streams using a provided m3u8 URL
- Ability to start new streams with Thetacloud account credentials
- Asynchronous processing of video streams for transcription
- Storage of transcription data in a filesystem, organized by unique task IDs
- Real-time display of video and transcription using HLS (HTTP Live Streaming)
- Support for multiple concurrent transcription viewers (currently set to 2)
- Customizable Timeouts for the transcription process (like process first 10 minutes of the video)

## Information for running:
### Viewing with Live Transcription:
- m3u8 url with valid stream already running

### Starting a Stream
- Account ID
- Account Key
- Stream Name
- Then using external tools a stream can be started with the above configuration

## Infra:
- Unique task id is formed for above configuration
- Ingestor Server (receives the stream and forms m3u8 url)
- Transcription Server (receives the m3u8 url and transcribes the video on the fly)
- All above data is stored in a filesystem with the task id as the directory name. A set is used to store which tasks are currently running. This is used to check if the task is already running or not.
- Asynchronously get the transcription and show it along the video stream using the HLS medium.

## Running the Server
To run the server, first of all clone the repo, make sure docker is installed and just run the following commands:
```bash
cd server
sudo sh start-docker.sh
```
This will setup the server which will be available at your http://localhost:80

## Running the Client
To run the client, first of all clone the repo, make sure nodejs, pnpm is installed and just run the following commands:
```bash
cd transcription-app
pnpm i
```
Create a .env file in the root of the transcription-app folder and add the following:
```bash
VITE_API_URL=http://<URL>
```

Then run the following command:
```bash
pnpm run dev
```

NOTE: you can also use `npm` instead of `pnpm`. But `pnpm` is recommended for faster installation and better caching.