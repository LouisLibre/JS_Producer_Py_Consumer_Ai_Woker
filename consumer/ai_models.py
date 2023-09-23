import time
import redis
import torch
import whisperx
import os
import base64
import json
from io import BytesIO
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Task timed out")

def extract_segments(segments_list):
    resp = []
    for seg in segments_list:
        resp.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': seg['text']
        })
    return resp

def whisperx_async_transcribe(job_content):

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(285)  # This value should be less than the RQ job timeout

    try:
        print(f" [x] Transcribing {job_content['fileName']} with full path: {job_content['filePath']}")
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        print(f"HELLO; CUDA available? {torch.cuda.is_available()}, device: {device}")
        model = whisperx.load_model("large", device)
        print(f"GOODBYE;")
        language = "en"

        # This step is probably not neccesary, just use the original file
        audio_file_name = job_content["filePath"]
        result = model.transcribe(audio_file_name, language=language)
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result_aligned = whisperx.align(result["segments"], model_a, metadata, audio_file_name, device)

        response = {
            'word_segments': result_aligned["word_segments"],
            'paragraphs': extract_segments(result_aligned['segments'])
        }

        # mock transcript result
        transcript = response;

        r = redis.StrictRedis(host='localhost', port=6379, db=0);
        # stringify the transcript

        r.set(job_content['fileName'], json.dumps(transcript));
        print(f" [x] Job done: {job_content['fileName']}");
    except TimeoutError:
        print(f" [x] Job timed out: {job_content['fileName']}");
        r = redis.StrictRedis(host='localhost', port=6379, db=0);
        r.set(job_content['fileName'], "TIMEDOUT");
    except Exception as e:
        print(f" [x] Job failed: {job_content['fileName']}");
        print(e)
        r = redis.StrictRedis(host='localhost', port=6379, db=0);
        r.set(job_content['fileName'], f"UNKNOWN_ERROR: {str(e)}");
    finally:
        signal.alarm(0)

def download_model():
    print("Downloading model")
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model = whisperx.load_model("large", device)
    print("Downloaded")

if __name__ == "__main__":
    download_model()
