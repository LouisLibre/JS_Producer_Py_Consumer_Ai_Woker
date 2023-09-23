import redis
import json
from rq import Queue

from ai_models import whisperx_async_transcribe

r = redis.StrictRedis(host='localhost', port=6379, db=0)
listQueue = 'mediaFilesQueue';
# Setting up RQ Queue
rq_queue = Queue(connection=r);
while True:
    _, job_data = r.brpop(listQueue);
    job = json.loads(job_data);
    # Enqueue the job to RQ
    rq_queue.enqueue(whisperx_async_transcribe, job, timeout='5m');
    print(f" [x] Received job with fileName: {job['fileName']}");
