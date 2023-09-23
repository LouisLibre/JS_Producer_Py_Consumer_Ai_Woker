import * as redis from 'redis';
import path from 'path';

const client = redis.createClient();

await client.connect();

client.on('error', (error) => {
  console.error(`Redis client not connected to the server: ${error}`);
});

const listQueue = 'mediaFilesQueue';

// Mock that we have an order to transcribe a video the user uploaded
//
// Read an argument from the user cli indicating the path to the video

// if the user doesn't provide a path, cancel the program

if (process.argv.length !== 3) {
  console.log('Please provide a path to the video');
  process.exit(1);
}

const filePath = process.argv[2];
// Can you make the filePath not relative, but absolute?
const absoluteFilePath = path.resolve(filePath);

const fileName = filePath.split('/').pop();

const transcribeVideoOrder = {
  filePath: absoluteFilePath,
  fileName: fileName
}

// register key-value pair in redis for fileName and filePath

try {
  await client.set(fileName, `ENQUEUED: ${absoluteFilePath}`);
  const _ = await client.lPush(listQueue, JSON.stringify(transcribeVideoOrder));
} catch (e) {
  console.error("Failed to LPUSH to queue:", e);
}
console.log(" [x] Sent %s for transcription", transcribeVideoOrder['filePath']);

// disconnect the client
await client.quit();

process.exit(0);
