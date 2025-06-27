from redis import Redis
from rq import Queue

# Initialize a Redis connection and create a queue
# this queue will internally use Redis as a message broker
# 'valkey' is the hostname of the Redis service in docker-compose.yml
q = Queue(connection=Redis(host='valkey', port=6379))