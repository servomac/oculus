import redis
import requests
import time

from datetime import datetime, timedelta
from docker import Client
from docker.errors import DockerException
from flask import Flask, redirect, render_template, url_for
from json import loads

from settings import DOCKER_BASE_URL
from settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from settings import REDIS_KEY, REDIS_KEY_TIMESTAMP

app = Flask(__name__)
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


class ConnectionError(Exception):
    def __init__(self, strerror):
        self.strerror = strerror

    def __str__(self):
        return str(self.strerror)


class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs


def retrieve(container_id, resource, instant):
    """ Obtain the data stored in Redis.
        Keyword arguments:
         - container_id: the desired container_id
         - resource: 'cpu', 'mem' or 'net'
         - instant: an specific datetime
    """
    r = redis.Redis(connection_pool=redis_pool)
    key = REDIS_KEY.format(timestamp=instant.strftime(REDIS_KEY_TIMESTAMP),
                           container_id=container_id,
                           resource=resource)
    value = r.get(key)

    if value != None:
        if resource == 'mem':
            # convert bytes to MB (memory usage)
            value = int(value) / (1024.0)**2
        elif resource == 'net':
            # return a dictionary
            value = loads(value)

    return value



@app.route('/')
def main_page():
    return redirect(url_for('containers'))

@app.route('/containers')
def containers():
    try:
        c = Client(base_url=DOCKER_BASE_URL, version='auto')
        containers = c.containers()

        for c in containers:
            # 12 initial characters of the hash identifying the container
            container_id = c["Id"][:12]
            for resource in ['cpu', 'mem']:
                c[resource] = retrieve(container_id,
                                       resource,
                                       datetime.now()-timedelta(minutes=1))

    except DockerException as e:
        error_msg = "Docker it's down."
        return render_template('overview.html', error=error_msg, status_msg=e)
    except redis.exceptions.ConnectionError as e:
        # TODO
        pass

    return render_template('overview.html', containers=containers)


@app.route('/container/<container_id>')
def describe_container(container_id):
    data = {}
    data['time'] = []
    minutes_range = 60      #TODO FIXME madafaka

    # obtain timeseries from redis
    try:
        #with Timer(verbose=True) as t:
        for resource in ['cpu', 'mem', 'net']:
            data[resource] = []
            for delta in range(60):
                timestamp = datetime.now() - timedelta(minutes=delta)
                value = retrieve(container_id, resource, timestamp)
                if value:
                    data[resource].append(value)

                data['time'].append(timestamp.strftime('%Y-%m-%d %H:%M'))


        # construct lists from list of jsons (network)
        data['net'] = {
            'tx': [x['TxBps'] for x in data['net']],
            'rx': [x['RxBps'] for x in data['net']],
            'tx_err': [x['Transmit']['Errs'] for x in data['net']],
            'rx_err': [x['Received']['Errs'] for x in data['net']],
        }
    except redis.exceptions.ConnectionError as e:
        data['error'] = 'Unable to obtain data about the container. [{}]'.format(e)


    # feed the template with the retrieved data
    return render_template('container.html', data=data, name=container_id,
                           items=['CPU', 'Memory'])


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
