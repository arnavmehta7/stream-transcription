from time import time
from faster_whisper import WhisperModel
import numpy as np
from stream.open_stream import open_stream
from .buffer import RingBuffer
from datetime import datetime
from whisper.audio import SAMPLE_RATE
import whisper
import torch


def load_normal_whisper():
    return whisper.load_model("small")

def load_faster_whisper():
    return WhisperModel("small", compute_type="int8")

def load_hf_whisper():
    from transformers import pipeline
    return pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-tiny",
        torch_dtype=torch.float16,
        # device="cuda:0", # or mps for Mac devices
        device="mps", # or mps for Mac devices
        # model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
    )

def transcribe_audio_using_hf_model(pipe, file_name: str):
    outputs = pipe(
        file_name,
        chunk_length_s=30,
        batch_size=24,
        return_timestamps=False,
    )
    return outputs["text"].strip()


model = load_normal_whisper()


def transcribe_video(url,language=None, interval=2, history_buffer_size=0, preferred_quality="audio_only",
         use_vad=True, direct_url=True, **decode_options):

    n_bytes = interval * SAMPLE_RATE * 2  # Factor 2 comes from reading the int16 stream as bytes
    audio_buffer = RingBuffer((history_buffer_size // interval) + 1)
    previous_text = RingBuffer(history_buffer_size // interval)
    print("Loading model...")

    if use_vad:
        from .vad import VAD
        vad = VAD()

    print("Opening stream...")
    ffmpeg_process, streamlink_process = open_stream(url, direct_url, preferred_quality)

    # def handler(signum, frame):
    #     ffmpeg_process.kill()
    #     if streamlink_process:
    #         streamlink_process.kill()
    #     sys.exit(0)
        
    # signal.signal(signal.SIGINT, handler)
    print(">>> Running Inference")
    try:
        while ffmpeg_process.poll() is None:
            s = time()
            # Read audio from ffmpeg stream
            in_bytes = ffmpeg_process.stdout.read(n_bytes)
            e = time()
            
            print(f'>> time to read first bytes: {e-s}')
            if not in_bytes:
                break

            audio = np.frombuffer(in_bytes, np.int16).flatten().astype(np.float32) / 32768.0
            if use_vad and vad.no_speech(audio):
                print(f'{datetime.now().strftime("%H:%M:%S")}')
                continue
            audio_buffer.append(audio)
            
            dur_audio = len(audio) / SAMPLE_RATE
            print(f'{datetime.now().strftime("%H:%M:%S")} {dur_audio} seconds')
            # Decode the audio
            clear_buffers = False

            # For normal whisper
            start = time()
            result = model.transcribe(np.concatenate(audio_buffer.get_all()),
                                        prefix="".join(previous_text.get_all()),
                                        language=language,
                                        without_timestamps=True,
                                        **decode_options)
            end = time()
            decoded_language = "" if language else "(" + result.get("language") + ")"
            decoded_text = result.get("text")
            new_prefix = ""
            for segment in result["segments"]:
                if segment["temperature"] < 0.5 and segment["no_speech_prob"] < 0.6:
                    new_prefix += segment["text"]
                else:
                    # Clear history if the translation is unreliable, otherwise prompting on this leads to
                    # repetition and getting stuck.
                    clear_buffers = True


            # For faster whisper
            # start = time()
            # segments, info = model.transcribe(np.concatenate(audio_buffer.get_all()),
            #                             prefix="".join(previous_text.get_all()),
            #                             language=language,
            #                             without_timestamps=True,
            #                             **decode_options)
            # end = time()
            # decoded_language = "" if language else "(" + info.get("language") + ")"
            # decoded_text = "".join([segment.text for segment in segments])
            # new_prefix = decoded_text
            
            
            previous_text.append(new_prefix)

            if clear_buffers or previous_text.has_repetition():
                audio_buffer.clear()
                previous_text.clear()
                
            # print(f'{datetime.now().strftime("%H:%M:%S")} {decoded_language} {decoded_text}, time taken: {end-start} seconds')
            yield f'{datetime.now().strftime("%H:%M:%S")} {decoded_text}\n'

        print("Stream ended")
    finally:
        ffmpeg_process.kill()
        if streamlink_process:
            streamlink_process.kill()

        
if __name__ == "__main__":
    # transcribe_video("a.mp3")
    # list(transcribe_video(url="files/output.m3u8", direct_url=True, language="en"))
    # asyncio.run(print_transcripts("https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8"))
    # main(
    #     url="https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
    #     model="tiny",
    #     language="en",
    #     direct_url=True,
    # )
    for text in transcribe_video(
        url="https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8",
        language="en",
        direct_url=True,
    ):
        print(text)
        
