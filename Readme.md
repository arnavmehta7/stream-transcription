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
- All above data is stored in a filesystem with the task id as the directory name
- Asynchronously get the transcription and show it along the video stream using the HLS medium.

