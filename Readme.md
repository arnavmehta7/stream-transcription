## Generate Live Transcript of any stream on Thetacloud


## User Configuration:
### Viewing with Live Transcription:
- m3u8 url with valid stream already running

### Starting a Stream
- Account ID
- Account Key
- Stream Name
- Then using external tools a stream can be started with the above configuration

### Infra:
- Unique task id is formed for above configuration
- Ingestor Server (receives the stream and forms m3u8 url)
- Transcription Server (receives the m3u8 url and transcribes the video on the fly)
- All above data is stored in a filesystem with the task id as the directory name. A set is used to store which tasks are currently running. This is used to check if the task is already running or not.
- Asynchronously get the transcription and show it along the video stream using the HLS medium.


## Running Server
To run the server, first of all clone the repo, make sure docker is installed and just run the following commands:
```bash
cd server
sudo sh start-docker.sh
```
This will setup the server which will be available at your http://localhost:80

## Running Client
To run the client, first of all clone the repo, make sure nodejs, pnpm is installed and just run the following commands:
```bash
cd transcription-app
pnpm i
pnpm run dev
```
NOTE: you can also use `npm` instead of `pnpm`. But `pnpm` is recommended for faster installation and better caching.