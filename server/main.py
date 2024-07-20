from typing import Optional
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import os
import time
from transcription.create_transcription import transcribe_video
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
MAX_TASK_DURATION = 60 * 10 # 10 min
os.makedirs(DATA_DIR, exist_ok=True)

# Dictionary to track active tasks
active_tasks = {}

def get_task_base_dir_path(task_id: str):
    base_dir = os.path.join(DATA_DIR, task_id)
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

# Simulated function to update transcript and translation
def update_transcript_from_input(task_id: str, m3u8_url: str, max_task_duration: int):
    s = time.time()
    transcript_path = os.path.join(get_task_base_dir_path(task_id), "transcript.txt")
    for transcript in transcribe_video(m3u8_url, direct_url=True, language="en"):
        print(">>>> transcript", transcript)
        e = time.time()
        if e - s >= max_task_duration:
            print(f"Task {task_id} stopped")
            break
        with open(transcript_path, "a") as transcript_file:
            transcript_file.write(f"{transcript}\n")
            transcript_file.flush()
        time.sleep(1)  # Simulate delay
    print(f">>>> removing from the active tasks: {m3u8_url}")
    del active_tasks[m3u8_url]


class StartTaskPayload(BaseModel):
    task_id: Optional[str] = str(uuid.uuid4())
    m3u8_url: str
    
@app.post("/start_task")
async def start_task(payload: StartTaskPayload, background_tasks: BackgroundTasks):
    m3u8_url = payload.m3u8_url
    task_id = payload.task_id  # type: str
     
    # Check if the m3u8_url is already being processed
    if m3u8_url in active_tasks:
        return {"message": "Task already running", "task_id": active_tasks[m3u8_url]}

    active_tasks[m3u8_url] = task_id  # Track the task
    background_tasks.add_task(update_transcript_from_input, task_id, m3u8_url, max_task_duration=MAX_TASK_DURATION)

    return {"message": "Task started", "task_id": task_id}

@app.get("/transcript/{task_id}")
async def get_transcript(task_id: str):
    transcript_path = os.path.join(get_task_base_dir_path(task_id), "transcript.txt")
    s = time.time()
    def transcript_stream():
        while True:
            if not os.path.exists(transcript_path): 
                time.sleep(1)
                e = time.time()
                if e - s >= MAX_TASK_DURATION:
                    break
                yield ""
            else:
                with open(transcript_path, "r") as f:
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(1)
                            continue
                        e = time.time()
                        if e - s >= MAX_TASK_DURATION:
                            break
                        yield line

    return StreamingResponse(transcript_stream(), media_type="text/event-stream")

# Run the app with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)