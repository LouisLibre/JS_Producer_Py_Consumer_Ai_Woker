from rq import Worker, Queue, Connection
import redis

listen = ['default'];

r = redis.StrictRedis(host='localhost', port=6379, db=0);

if __name__ == '__main__':
    with Connection(r):
        worker = Worker(list(map(Queue, listen)));
        worker.work();
