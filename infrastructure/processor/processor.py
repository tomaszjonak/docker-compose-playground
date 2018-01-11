import redis
import logging
import random
import time
import prometheus_client as pclient

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s|%(threadName)s] %(levelname)s: %(message)s')


red_con = redis.Redis('queue')
try:
    response = red_con.ping()
    logging.debug('Redis connection established')
except redis.ConnectionError as e:
    red_con = None
    logging.exception(e)
    exit(-1)

tasks_processed = pclient.Counter('tasks_processed', "Amount of tasks processed")
pclient.start_http_server(addr='0.0.0.0', port=8080)

while True:
    task = red_con.blpop('queue:tasks')
    logging.debug('Processing task ({})'.format(task))
    time.sleep(random.uniform(0, 5))
    logging.info('Task processing done')
    tasks_processed.inc()
