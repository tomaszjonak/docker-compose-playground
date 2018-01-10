import redis
import bottle
import logging
import json
import hashlib
import random
import time
import prometheus_client as pclient

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s|%(threadName)s] %(levelname)s: %(message)s')

fetcher = bottle.default_app()
fetcher.config.load_config('./config.conf')
bottle.BaseTemplate.defaults['PREFIX_URL'] = fetcher.config.get('global.prefix', '')

redis_host = fetcher.config.get('redis.host', 'localhost')
redis_port = int(fetcher.config.get('redis.port', 8080))
red_con = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

fail_counter = pclient.Counter('failed_requests', 'Failed requests', ['method', 'error_type'])
success_counter = pclient.Counter('success_requests', 'Succeeded requests', ['method'])

try:
    response = red_con.ping()
    logging.debug('Redis connection established')
except redis.ConnectionError as e:
    red_con = None
    logging.exception(e)

m = hashlib.sha256()
secret = fetcher.config.get('global.secret', 'correct horse battery staple').encode('utf8')
m.update(secret)
secret_hash = m.hexdigest()
logging.debug('Hash calculated ({})'.format(secret_hash))


@bottle.route('/', method='GET')
def health_check():
    if red_con:
        success_counter.labels('GET').inc()
        return 'Awsum m8'
    else:
        fail_counter.labels('GET', 'redis_failure').inc()
        return 'No redis connection'


@bottle.route('/', method='POST')
def handle_task():
    logging.info('Processing request (source: {})'.format(bottle.request.remote_addr))
    postdata = bottle.request.body.read().decode()

    try:
        decoded_data = json.loads(postdata)
    except Exception as e:
        logging.exception(e)
        fail_counter.labels('POST', 'payload_decode').inc()
        return bottle.HTTPError(400, 'Not a json formatted post')

    if 'secret' not in decoded_data:
        fail_counter.labels('POST', 'no_secret').inc()
        return bottle.HTTPError(400, 'Required parameter missing')

    if decoded_data['secret'] != secret_hash:
        fail_counter.labels('POST', 'wrong_secret').inc()
        return bottle.HTTPError(403, 'Invalid secret provided')
    time.sleep(random.uniform(0, 5))
    if not red_con:
        fail_counter.labels('POST', 'redis_failure').inc()
        return bottle.HTTPError(503, 'Redis malfunction')

    task_data = {k: v for k, v in decoded_data.items() if k not in ('secret',)}
    logging.info('Putting task into queue ({})'.format(task_data))
    red_con.rpush('queue:tasks', task_data)
    success_counter.labels('POST').inc()


# start metrics daemon
monitoring_port = int(fetcher.config.get('monitoring.port', 8080))
logging.debug('Starting monitoring service (port: {})'.format(monitoring_port))
pclient.start_http_server(addr='0.0.0.0', port=monitoring_port)

app_host = fetcher.config.get('frontend.host', 'localhost')
app_port = int(fetcher.config.get('frontend.port', 80))
logging.debug('Listening ({})'.format((app_host, app_port)))
fetcher.run(host=app_host, port=app_port)
