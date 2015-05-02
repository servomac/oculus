import redis
import requests

from celery import Celery
from datetime import datetime, timedelta
from flask import Flask, render_template

from settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from settings import REDIS_KEY, REDIS_KEY_TIMESTAMP

app = Flask(__name__)

celery = Celery('tasks')
celery.config_from_object('celeryconfig')


@app.route('/container/<container_id>')
def describe_container(container_id):
    data = {}
    data['time'] = []

    # obtain timeseries from redis
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    for resource in ['cpu', 'mem']:
        data[resource] = []
        for delta in range(60):
            timestamp = datetime.now() - timedelta(minutes=delta)
            key = REDIS_KEY.format(timestamp=timestamp.strftime(REDIS_KEY_TIMESTAMP),
                                   container_id=container_id, resource=resource)
            value = r.get(key)
            data[resource].append(value)
            data['time'].append(timestamp.strftime('%Y-%m-%d %H:%M'))

    # feed the template with the retrieved data
    return render_template('container.html', data=data, name=container_id,
                           items=['CPU', 'Memory'])


if __name__ == '__main__':
    app.run(debug=True)
