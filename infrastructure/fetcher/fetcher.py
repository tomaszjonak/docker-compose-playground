import redis
import bottle
import logging
import json
import hashlib
import random
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s|%(threadName)s] %(levelname)s: %(message)s')

fetcher = bottle.default_app()
fetcher.config.load_config('./config.conf')
bottle.BaseTemplate.defaults['PREFIX_URL'] = fetcher.config.get('global.prefix', '')

redis_host = fetcher.config.get('redis.host', 'localhost')
redis_port = int(fetcher.config.get('redis.port', 8080))
red_con = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

try:
    response = red_con.ping()
    # red_con.rpush('queue:tasks', {'x': 'D'})
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
    return 'Awsum m8' if red_con else 'No redis connection'


@bottle.route('/', method='POST')
def handle_task():
    logging.info('Processing request (source: {})'.format(bottle.request.remote_addr))
    postdata = bottle.request.body.read().decode()

    try:
        decoded_data = json.loads(postdata)
    except Exception as e:
        logging.exception(e)
        return bottle.HTTPError(400, 'Not a json formatted post')

    if 'secret' not in decoded_data:
        return bottle.HTTPError(400, 'Required parameter missing')

    if decoded_data['secret'] != secret_hash:
        return bottle.HTTPError(403, 'Invalid secret provided')
    time.sleep(random.uniform(0, 5))

    if not red_con:
        return bottle.HTTPError(503, 'Redis malfunction')

    task_data = {k: v for k, v in decoded_data.items() if k not in ('secret',)}
    logging.info('Putting task into queue ({})'.format(task_data))
    red_con.rpush('queue:tasks', task_data)


app_host = fetcher.config.get('frontend.host', 'localhost')
app_port = int(fetcher.config.get('frontend.port', 80))
logging.debug('Listening ({})'.format((app_host, app_port)))
fetcher.run(host=app_host, port=app_port)
