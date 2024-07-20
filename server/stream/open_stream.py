from whisper.audio import SAMPLE_RATE
import ffmpeg
import sys
import subprocess

def open_stream(stream, direct_url, preferred_quality):
    if direct_url:
        try:
            process = (
                ffmpeg.input(stream, loglevel="panic")
                .output("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=SAMPLE_RATE)
                .run_async(pipe_stdout=True)
            )
            # ffplay_cmd = [
            #     "ffplay",
            #     "-nodisp",
            #     "-autoexit",
            #     "-i", stream
            # ]
            # ffplay_process = subprocess.Popen(ffplay_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        return process, None

    import streamlink
    import threading
    stream_options = streamlink.streams(stream)
    if not stream_options:
        print("No playable streams found on this URL:", stream)
        sys.exit(0)

    option = None
    for quality in [preferred_quality, 'audio_only', 'audio_mp4a', 'audio_opus', 'best']:
        if quality in stream_options:
            option = quality
            break
    if option is None:
        # Fallback
        option = next(iter(stream_options.values()))

    def writer(streamlink_proc, ffmpeg_proc):
        while (not streamlink_proc.poll()) and (not ffmpeg_proc.poll()):
            try:
                chunk = streamlink_proc.stdout.read(1024)
                ffmpeg_proc.stdin.write(chunk)
            except (BrokenPipeError, OSError):
                pass

    cmd = ['streamlink', stream, option, "-O"]
    streamlink_process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    try:
        ffmpeg_process = (
            ffmpeg.input("pipe:", loglevel="panic")
            .output("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=SAMPLE_RATE)
            .run_async(pipe_stdin=True, pipe_stdout=True)
        )
    except ffmpeg.Error as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    thread = threading.Thread(target=writer, args=(streamlink_process, ffmpeg_process))
    thread.start()
    return ffmpeg_process, streamlink_process
