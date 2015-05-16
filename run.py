import redis
import requests
import time

from apscheduler.scheduler import Scheduler
from datetime import datetime, timedelta
from docker import Client
from docker.errors import DockerException
from flask import Flask, redirect, render_template, url_for
from json import loads

from publisher.settings import DOCKER_BASE_URL
from publisher.settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from publisher.settings import REDIS_KEY, REDIS_KEY_TIMESTAMP

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

class OculusDocker(object):
    def __init__(self):
        self.client = Client(base_url=DOCKER_BASE_URL, version='auto')

    def containers_ids(self):
        for c in self.client.containers():
            yield c['Id'][:12]


def retrieve(container_id, resource, instant):
    """ Obtain the data stored in Redis.
        args:
         - container_id: the desired container_id
         - resource: 'cpu', 'mem' or 'net'
         - instant: a datetime instance
    """
    r = redis.Redis(connection_pool=redis_pool)
    key = REDIS_KEY.format(timestamp=instant.strftime(REDIS_KEY_TIMESTAMP),
                           container_id=container_id,
                           resource=resource)
    value = loads(r.get(key))

    return value



@app.route('/')
def main_page():
    return redirect(url_for('containers'))

@app.route('/containers')
def containers():
    try:
        c = Client(base_url=DOCKER_BASE_URL, version='auto')
        containers = c.containers()

        d = OculusDocker()
        c = {}
        for container_id in list(d.containers_ids()):
            # 12 initial characters of the hash identifying the container
            #container_id = c["Id"][:12]
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


def convert_ticks_to_usage(cpu_stats):
    """ convert a list of {'system_cpu_usage': 771430350000000, 'cpu_usage': {'usage_in_kernelmode': 46800000000, 'percpu_usage': [29361095473, 29469353200, 7072412908, 7714245950], 'total_usage': 73617107531, 'usage_in_usermode': 18820000000}, 'throttling_data': {'throttled_periods': 0, 'periods': 0, 'throttled_time': 0}}
    """
    ltotalticks = [int(s['cpu_usage']['total_usage']) for s in cpu_stats]
    total = sum(ltotalticks)
    #lusage = [ticks*100.0/total for ticks in ltotalticks]
    #lusage = reduce(lambda x, y: (y-x)/total, lusage, 0)

    # iterate by pairs
    lusage = [(x-y) for x, y in zip(ltotalticks[:-1], ltotalticks[1:])]

    return lusage

@app.route('/container/<container_id>')
def describe_container(container_id):
    data = {}
    data['time'] = []
    minutes_range = 60      #TODO FIXME madafaka

    # obtain timeseries from redis
    try:
        #with Timer(verbose=True) as t:
        for resource in ['cpu_stats', 'memory_stats', 'network', 'blkio_stats']:
            data[resource] = []
            for delta in range(60):
                timestamp = datetime.now() - timedelta(minutes=delta)
                value = retrieve(container_id, resource, timestamp)
                if value:
                    data[resource].append(value)

                data['time'].append(timestamp.strftime('%Y-%m-%d %H:%M'))


#       # construct lists from list of jsons (network)
#       data['net'] = {
#           'tx': [x['TxBps'] for x in data['net']],
#           'rx': [x['RxBps'] for x in data['net']],
#           'tx_err': [x['Transmit']['Errs'] for x in data['net']],
#           'rx_err': [x['Received']['Errs'] for x in data['net']],
#       }
    except redis.exceptions.ConnectionError as e:
        data['error'] = 'Unable to obtain data about the container. [{}]'.format(e)


#{'max_usage': 16216064, 'stats': {'mapped_file': 1626112, 'total_pgpgout': 14738, 'total_pgfault': 7569, 'active_file': 2084864, 'pgpgin': 16379, 'total_unevictable': 0, 'total_cache': 2351104, 'rss_huge': 2097152, 'pgpgout': 14738, 'total_mapped_file': 1626112, 'inactive_anon': 4096, 'inactive_file': 245760, 'cache': 2351104, 'pgmajfault': 130, 'unevictable': 0, 'hierarchical_memory_limit': 18446744073709551615, 'writeback': 0, 'total_inactive_file': 245760, 'pgfault': 7569, 'total_active_file': 2084864, 'active_anon': 6479872, 'rss': 6463488, 'total_writeback': 0, 'total_pgpgin': 16379, 'total_inactive_anon': 4096, 'total_pgmajfault': 130, 'total_rss': 6463488, 'total_active_anon': 6479872, 'total_rss_huge': 2097152}, 'failcnt': 0, 'usage': 8814592, 'limit': 4033351680}


    data['cpu'] = {
            'usage' : convert_ticks_to_usage(data['cpu_stats']),
        }
    data['mem'] = {
            'usage' : [float(s['usage'])/(1024.0**2.0) for s in data['memory_stats']]
        }
    data['net'] = []

    # feed the template with the retrieved data
    return render_template('container.html', data=data, name=container_id,
                           items=['CPU', 'Memory'])


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def poll():
    print "Hello World i'm a periodic task"

#@app.before_first_request
#def initialize():
#    apsched = Scheduler()
#    apsched.start()

    #d = OculusDocker()
    #for c in list(d.containers_ids()):
    #    apsched.


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

