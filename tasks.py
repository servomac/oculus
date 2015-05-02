import redis
import requests
from celery import Celery
from datetime import datetime
from json import dumps

from settings import container_id, API_URL
from settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from settings import REDIS_KEY, REDIS_KEY_TIMESTAMP, REDIS_EXPIRE_TIME

celery = Celery('tasks')
celery.config_from_object('celeryconfig')


def construct_request(api_url, container_id, dest):
    return '{api}/containers/{container}/{dest}'.format(api=api_url,
                                          container=container_id,
                                          dest=dest)

@celery.task
def poll(resource):
    print resource
    req_url = construct_request(API_URL, container_id, resource)
    req = requests.get(req_url)

    if req.status_code != 200:
        raise Exception('Bad status code')

    if req.text == '-1' or req.text == 'id not found':
        raise Exception('Unknown container {} [API Response: {}]'.format(container_id, req.text))

    # save the results polled from the API to redis
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    key = REDIS_KEY.format(timestamp=datetime.now().strftime(REDIS_KEY_TIMESTAMP),
                           container_id=container_id, resource=resource)

    value = dumps(req.json()) if resource == 'net' else req.text
    print "{}: {}".format(key, value)
    r.set(key, value)
    r.expire(key, REDIS_EXPIRE_TIME)
