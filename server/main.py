from typing import Optional
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import os
import time
import threading
from server.transcription.create_transcription import transcribe_video
from fastapi.middleware.cors import CORSMiddleware
# from translation import translate_text

translate_text = lambda *args, **kwargs: ""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust the allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods including POST
    allow_headers=["*"],
)
# Directory to store transcripts and translations
DATA_DIR = "data"
MAX_TASK_DURATION = 60 # seconds
os.makedirs(DATA_DIR, exist_ok=True)

# Dictionary to track active tasks
active_tasks = {}

def get_task_base_dir_path(task_id: str):
    base_dir = os.path.join(DATA_DIR, task_id)
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

# Simulated function to update transcript and translation
def update_transcript_and_translation(task_id: str, m3u8_url: str, target_languages: list = [], stop_event: threading.Event = None):
    transcript_path = os.path.join(get_task_base_dir_path(task_id), "transcript.txt")
    translation_paths = {lang: os.path.join(get_task_base_dir_path(task_id), f"translation_{lang}.txt") for lang in target_languages}
    # while True:
    #     time.sleep(1)
    #     r_text = "Hello, how are you?"
    #     with open(transcript_path, "a") as transcript_file:
    #         transcript_file.write(f"{r_text}\n")
    #         transcript_file.flush()
    for transcript in transcribe_video(m3u8_url, direct_url=True, language="en"):
        print(">>>> transcript", transcript)
        if stop_event.is_set():
            print(f"Task {task_id} stopped")
            break
        with open(transcript_path, "a") as transcript_file:
            transcript_file.write(f"{transcript}\n")
            transcript_file.flush()
        for lang in target_languages:
            translation = translate_text(transcript, lang)
            with open(translation_paths[lang], "a") as translation_file:
                translation_file.write(f"{translation}\n")
        time.sleep(1)  # Simulate delay

def stop_task_after_duration(stop_event: threading.Event, duration: int):
    time.sleep(duration)
    stop_event.set()


from pydantic import BaseModel

class StartTaskPayload(BaseModel):
    task_id: Optional[str] = str(uuid.uuid4())
    m3u8_url: str
    target_languages: Optional[list] = []
    
@app.post("/start_task")
async def start_task(payload: StartTaskPayload, background_tasks: BackgroundTasks):
    m3u8_url = payload.m3u8_url
    task_id = payload.task_id  # type: str
     
    # Check if the m3u8_url is already being processed
    if m3u8_url in active_tasks:
        return {"message": "Task already running", "task_id": active_tasks[m3u8_url]}

    stop_event = threading.Event()
    active_tasks[m3u8_url] = task_id  # Track the task
    background_tasks.add_task(update_transcript_and_translation, task_id, m3u8_url, stop_event=stop_event)
    background_tasks.add_task(stop_task_after_duration, stop_event, MAX_TASK_DURATION)

    # Remove the task from active_tasks after completion
    def remove_task():
        stop_event.wait()
        del active_tasks[m3u8_url]

    background_tasks.add_task(remove_task)

    return {"message": "Task started", "task_id": task_id}

@app.get("/transcript/{task_id}")
async def get_transcript(task_id: str):
    transcript_path = os.path.join(get_task_base_dir_path(task_id), "transcript.txt")
    def transcript_stream():
        while True:
            if not os.path.exists(transcript_path): 
                time.sleep(1)
                yield ""
            else:
                with open(transcript_path, "r") as f:
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(1)
                            continue
                        yield line

    return StreamingResponse(transcript_stream(), media_type="text/event-stream")

@app.get("/translation/{task_id}/{language}")
async def get_translation(task_id: str, language: str):
    translation_path = os.path.join(get_task_base_dir_path(task_id), f"translation_{language}.txt")
    if not os.path.exists(translation_path):
        return {"message": "Translation not found"}

    def translation_stream():
        with open(translation_path, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                yield line

    return StreamingResponse(translation_stream(), media_type="text/event-stream")

# Run the app with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)