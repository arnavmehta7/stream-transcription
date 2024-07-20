from whisper.audio import SAMPLE_RATE
import ffmpeg
import sys
import subprocess

def open_stream(stream):
    try:
        process = (
            ffmpeg.input(stream, loglevel="panic")
            .output("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=SAMPLE_RATE)
            .run_async(pipe_stdout=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return process, None
